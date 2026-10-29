from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from .models import CustomUser, Parent
from .forms import ParentLoginForm, ParentSignUpForm
from .services import get_enrollments_from_parent, get_student_data_from_enrollment
from .localisation import KINSHASA

User = get_user_model()

def parent_login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("account:parent_account")
    
    form = ParentLoginForm(request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if getattr(user, "role", None) != CustomUser.Role.PARENT:
                    form.add_error("email", "Cette addresse email n'est pas associée à un compte parent.")
                else:
                    login(request, user)
                    return redirect("account:parent_account")
            else:
                # Generic error to prevent email enumeration
                form.add_error(None, "Email ou mot de passe incorrect.")
                
    return render(request, "accounts/parent_login.html", {"form": form})


def parent_sign_up(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("account:parent_account")
    
    form = ParentSignUpForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        role = CustomUser.Role.PARENT
        email = form.cleaned_data.get("email")
        phone_number = form.cleaned_data.get("phone_number")
        alternate_phone_number = form.cleaned_data.get("alternate_phone_number")
        
        township = form.cleaned_data.get("township")
        quater = form.cleaned_data.get("quater")
        street = form.cleaned_data.get("street")
        address = f"Commune de {township}, quartier {quater}, avenue / rue {street}"
        
        password = form.cleaned_data.get("password")
        
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name, last_name=last_name, role=role)
        Parent.objects.create(user=user, phone_number=phone_number, alternate_phone_number=alternate_phone_number, address=address)
        login(request, user)
        return redirect("account:parent_account")
        
    return render(request, "accounts/sign_up.html", {"form": form, "KINSHASA": KINSHASA})
    

@login_required
def parent_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("home:index")


@login_required(login_url="account:parent_login")
def parent_account(request: HttpRequest) -> HttpResponse:
    if getattr(request.user, "role", None) == CustomUser.Role.PARENT:
        try:
            parent = Parent.objects.get(user=request.user)
            data = {"student": []}
            enrollments = get_enrollments_from_parent(parent)
            
            for enrollment in enrollments:
                data["student"].append(
                    get_student_data_from_enrollment(enrollment)
                )
            
            return render(request, "accounts/parent_account.html", data)
        except Parent.DoesNotExist:
            return render(request, "accounts/bad_auth.html", {"error": "Aucun compte parent n'est associé à ce compte utilisateur."})
        
    return redirect("account:parent_login")