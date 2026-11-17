from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone
from unittest.mock import patch

from apps.accounts.models import CustomUser, Parent
from apps.finance.models import Fee, FeePayment
from apps.finance.saspay import PaymentError
from apps.students.models import (
    AcademicYear,
    Enrollment,
    SchoolClass,
    Student,
    StudentGuardian,
)


class FeePaymentRulesTests(TestCase):
    user: CustomUser
    school_class: SchoolClass
    other_class: SchoolClass
    enrollment: Enrollment
    fee: Fee

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = CustomUser.objects.create_user(
            username="accountant1", password="test-pass-123", role=CustomUser.Role.ACCOUNTANT
        )
        year: AcademicYear = AcademicYear.objects.create(
            name="2026-2027", start_date=date(2026, 9, 1), end_date=date(2027, 7, 15)
        )
        cls.school_class = SchoolClass.objects.create(name="6A")
        cls.other_class = SchoolClass.objects.create(name="6B")
        student: Student = Student.objects.create(
            admission_number="G001",
            first_name="Jean",
            last_name="Mbala",
            date_of_birth=date(2014, 3, 2),
            gender=Student.Gender.MALE,
        )
        cls.enrollment = Enrollment.objects.create(
            student=student, academic_year=year, school_class=cls.school_class
        )
        cls.fee = Fee.objects.create(
            school_class=cls.school_class,
            academic_year=year,
            name="Minerval",
            amount_due=Decimal("100.00"),
            currency=Fee.Currency.USD,
            created_by=cls.user,
        )

    def make_payment(self, receipt: str, **overrides: object) -> FeePayment:
        data: dict[str, object] = {
            "enrollment": self.enrollment,
            "fee": self.fee,
            "amount_paid": Decimal("40.00"),
            "payment_date": date(2026, 10, 1),
            "payment_method": FeePayment.PaymentMethod.CASH,
            "payment_currency": Fee.Currency.USD,
            "exchange_rate": Decimal("1"),
            "receipt_reference": receipt,
            "submitted_by": self.user,
        }
        data.update(overrides)
        return FeePayment.objects.create(**data)

    def test_fee_must_match_enrollment_class(self) -> None:
        other_fee: Fee = Fee.objects.create(
            school_class=self.other_class,
            academic_year=self.fee.academic_year,
            name="Minerval",
            amount_due=Decimal("90.00"),
            created_by=self.user,
        )
        with self.assertRaises(ValidationError):
            self.make_payment("R-001", fee=other_fee)

    def test_same_currency_requires_rate_one(self) -> None:
        with self.assertRaises(ValidationError):
            self.make_payment("R-002", exchange_rate=Decimal("2"))

    def test_different_currency_rejects_rate_one(self) -> None:
        with self.assertRaises(ValidationError):
            self.make_payment(
                "R-003",
                payment_currency=Fee.Currency.CDF,
                amount_paid=Decimal("28000.00"),
                exchange_rate=Decimal("1"),
            )

    def test_negative_amount_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.make_payment("R-004", amount_paid=Decimal("-5.00"))

    def test_database_blocks_verified_without_verifier(self) -> None:
        payment: FeePayment = self.make_payment("R-005")
        with self.assertRaises(IntegrityError), transaction.atomic():
            FeePayment.objects.filter(pk=payment.pk).update(status=FeePayment.Status.VERIFIED)

    def test_only_verified_payments_reduce_balance(self) -> None:
        self.make_payment("R-006")  # pending, must not count
        self.make_payment(
            "R-007",
            status=FeePayment.Status.VERIFIED,
            verified_by=self.user,
            verified_at=timezone.now(),
        )
        self.make_payment(
            "R-008",
            payment_currency=Fee.Currency.CDF,
            amount_paid=Decimal("28000.00"),
            exchange_rate=Decimal("0.0003571429"),
            status=FeePayment.Status.VERIFIED,
            verified_by=self.user,
            verified_at=timezone.now(),
        )
        # 40 USD verified + 28,000 CDF (= 10 USD) verified; the pending 40 is ignored.
        self.assertEqual(self.fee.outstanding_for(self.enrollment), Decimal("50.00"))


@override_settings(
    ROOT_URLCONF='apps.finance.urls',
    SASPAY_API_TOKEN='test-token',
    SASPAY_EXCHANGE_RATES={'USD_CDF': '2800'},
)
class FeePaymentViewTests(TestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(
            username='fee-parent',
            password='test-password',
            role=CustomUser.Role.PARENT,
        )
        parent = Parent.objects.create(
            user=self.user,
            phone_number='0812345678',
            address='Kinshasa',
        )
        year = AcademicYear.objects.create(
            name='2027-2028',
            start_date=date(2027, 9, 1),
            end_date=date(2028, 7, 15),
            is_current=True,
        )
        school_class = SchoolClass.objects.create(name='5A')
        student = Student.objects.create(
            admission_number='G002',
            first_name='Marie',
            last_name='Kabeya',
            date_of_birth=date(2015, 2, 1),
            gender=Student.Gender.FEMALE,
        )
        self.enrollment = Enrollment.objects.create(
            student=student,
            academic_year=year,
            school_class=school_class,
            status=Enrollment.Status.ENROLLED,
        )
        StudentGuardian.objects.create(
            parent=parent,
            student=student,
            relationship=StudentGuardian.Relationship.MOTHER,
        )
        self.fee = Fee.objects.create(
            school_class=school_class,
            academic_year=year,
            name='Minerval',
            amount_due=Decimal('100000.00'),
            currency=Fee.Currency.CDF,
            created_by=self.user,
        )
        self.client.force_login(self.user)
        self.url = f'/enrollment/{self.enrollment.pk}/pay/'

    @patch('apps.finance.views.collect_fee_payment')
    def test_valid_payment_is_sent_to_saspay_and_saved_pending(self, collect_payment) -> None:
        response = self.client.post(self.url, {
            'fee': self.fee.pk,
            'amount': '10.00',
            'currency': Fee.Currency.USD,
            'operator': 'vodacom_cd',
            'phone_number': '0812345678',
        })

        self.assertEqual(response.status_code, 202)
        payment = FeePayment.objects.get()
        self.assertEqual(payment.status, FeePayment.Status.PENDING)
        self.assertEqual(payment.exchange_rate, Decimal('2800'))
        self.assertEqual(payment.receipt_reference, response.json()['payment_reference'])
        collect_payment.assert_called_once()

    @patch('apps.finance.views.collect_fee_payment')
    def test_payment_exceeding_balance_is_rejected(self, collect_payment) -> None:
        response = self.client.post(self.url, {
            'fee': self.fee.pk,
            'amount': '40.00',
            'currency': Fee.Currency.USD,
            'operator': 'vodacom_cd',
            'phone_number': '0812345678',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('amount', response.json()['errors'])
        self.assertFalse(FeePayment.objects.exists())
        collect_payment.assert_not_called()

    @patch('apps.finance.views.collect_fee_payment')
    def test_unverified_enrollment_cannot_pay_fees(self, collect_payment) -> None:
        Enrollment.objects.filter(pk=self.enrollment.pk).update(
            status=Enrollment.Status.PENDING,
        )
        response = self.client.post(self.url, {
            'fee': self.fee.pk,
            'amount': '10.00',
            'currency': Fee.Currency.USD,
            'operator': 'vodacom_cd',
            'phone_number': '0812345678',
        })

        self.assertEqual(response.status_code, 409)
        self.assertFalse(FeePayment.objects.exists())
        collect_payment.assert_not_called()

    @override_settings(SASPAY_API_TOKEN='')
    @patch('apps.finance.views.collect_fee_payment')
    def test_missing_saspay_token_does_not_create_payment(self, collect_payment) -> None:
        response = self.client.post(self.url, {
            'fee': self.fee.pk,
            'amount': '10.00',
            'currency': Fee.Currency.USD,
            'operator': 'vodacom_cd',
            'phone_number': '0812345678',
        })

        self.assertEqual(response.status_code, 503)
        self.assertFalse(FeePayment.objects.exists())
        collect_payment.assert_not_called()

    @override_settings(SASPAY_EXCHANGE_RATES={})
    @patch('apps.finance.views.collect_fee_payment')
    def test_unconfigured_exchange_rate_is_rejected(self, collect_payment) -> None:
        response = self.client.post(self.url, {
            'fee': self.fee.pk,
            'amount': '10.00',
            'currency': Fee.Currency.USD,
            'operator': 'vodacom_cd',
            'phone_number': '0812345678',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('currency', response.json()['errors'])
        self.assertFalse(FeePayment.objects.exists())
        collect_payment.assert_not_called()

    @patch(
        'apps.finance.views.collect_fee_payment',
        side_effect=PaymentError("SasaPay ne répond pas pour le moment."),
    )
    def test_gateway_error_keeps_payment_pending_for_reconciliation(self, collect_payment) -> None:
        response = self.client.post(self.url, {
            'fee': self.fee.pk,
            'amount': '10.00',
            'currency': Fee.Currency.USD,
            'operator': 'vodacom_cd',
            'phone_number': '0812345678',
        })

        self.assertEqual(response.status_code, 502)
        payment = FeePayment.objects.get()
        self.assertEqual(payment.status, FeePayment.Status.PENDING)
        self.assertIn(payment.receipt_reference, response.json()['message'])
