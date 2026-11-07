

from .models import FeePayment

def soft_money_money_pay(amount_due: int, phone_number: int, operator: str) -> int:
    operator += " " + str(amount_due)
    return 0