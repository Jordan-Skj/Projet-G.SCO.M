from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from accounts.models import CustomUser
from finance.models import Fee, FeePayment
from students.models import AcademicYear, Enrollment, SchoolClass, Student


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