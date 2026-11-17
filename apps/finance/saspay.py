import json
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from django.conf import settings

from apps.accounts.models import CustomUser


class PaymentError(Exception):
    pass


BASE_URL = 'https://api.saspay.me/api/v1'


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def api_request(path: str, method: str, payload: dict | None = None) -> dict:
    token = settings.SASPAY_API_TOKEN
    if not token:
        raise PaymentError("Le service de paiement mobile n'est pas configuré.")

    request = Request(
        BASE_URL + path,
        method=method,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        data=json.dumps(payload).encode() if payload is not None else None,
    )

    try:
        with build_opener(NoRedirects).open(
            request,
            timeout=settings.SASPAY_TIMEOUT,
        ) as response:
            result = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        raise PaymentError("SasaPay ne répond pas pour le moment.") from None

    if not isinstance(result, dict) or result.get('success') is False:
        raise PaymentError(
            "Le paiement est indisponible pour le moment. "
            "Veuillez contacter le secrétariat pour payer en espèces."
        )

    data = result.get('data')
    if not isinstance(data, dict):
        raise PaymentError("Erreur de paiement : réponse SasaPay invalide.")

    return data


def softpay_request(
    country: str,
    amount: float,
    currency: str,
    description: str,
    customer_first_name: str,
    customer_last_name: str,
    customer_email: str,
    customer_phone: str,
    network: str,
) -> dict:
    return api_request('payments/softpay', 'POST', {
        "amount": amount,
        "currency": currency,
        "country": country,
        "network": network,
        "description": description,
        "customer": {
            "phone": customer_phone,
            "email": customer_email,
            "first_name": customer_first_name,
            "last_name": customer_last_name,
        },
    })


def collect_fee_payment(
    form_cleaned_data: dict,
    parent_user: CustomUser,
    payment_reference: str,
) -> dict:
    return softpay_request(
        country='CD',
        amount=float(form_cleaned_data['amount']),
        currency=form_cleaned_data['currency'],
        description=(
            f"Paiement de frais pour {form_cleaned_data['fee'].name} "
            f"(réf. {payment_reference})"
        ),
        customer_first_name=parent_user.first_name,
        customer_last_name=parent_user.last_name,
        customer_email=parent_user.email,
        customer_phone=form_cleaned_data['phone_number'],
        network=form_cleaned_data['operator'],
    )
