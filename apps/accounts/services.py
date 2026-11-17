from typing import Any
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.accounts.models import CustomUser, Parent
from apps.audit.models import Auditlog
from apps.audit.services import log_action

User = get_user_model()

def create_parent_user(form_data : dict[Any]) -> CustomUser:
    name = form_data.get('first_name')
    last_name = form_data.get('last_name')
    role = CustomUser.Role.PARENT
    email = form_data.get('email', '')
    phone_number = form_data.get('phone_number')
    alternate_phone_number = form_data.get('alternate_phone_number')
    
    township = form_data.get('township')
    quarter = form_data.get('quarter')
    street = form_data.get('street')
    address = f'Commune de {township}, quartier {quarter}, avenue / rue {street}'
    
    password = form_data.get('password')
    
    with transaction.atomic():
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name, last_name=last_name, role=role)
        parent = Parent.objects.create(
            user=user,
            phone_number=phone_number,
            alternate_phone_number=alternate_phone_number or None,
            address=address,
            gender=form_data['gender'],
        )
        log_action(actor=user, action=Auditlog.Action.CREATE, target=user)
        log_action(actor=user, action=Auditlog.Action.CREATE, target=parent)
        
    return user