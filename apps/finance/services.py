

from decimal import Decimal, InvalidOperation

from django.conf import settings


def get_exchange_rate(payment_currency: str, fee_currency: str) -> Decimal | None:
    if payment_currency == fee_currency:
        return Decimal('1')

    rates = getattr(settings, 'SASPAY_EXCHANGE_RATES', {})
    if not isinstance(rates, dict):
        return None

    configured_rate = rates.get(f'{payment_currency}_{fee_currency}')
    if configured_rate is None:
        return None

    try:
        rate = Decimal(str(configured_rate))
    except (InvalidOperation, TypeError, ValueError):
        return None

    if not rate.is_finite() or rate <= 0 or rate > Decimal('9999999999.9999999999'):
        return None

    try:
        rate = rate.quantize(Decimal('0.0000000001'))
    except InvalidOperation:
        return None
    return rate if rate > 0 else None


def soft_money_money_pay(amount_due: int, phone_number: int, operator: str) -> int:
    operator += " " + str(amount_due)
    return 0
