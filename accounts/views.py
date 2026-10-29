from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from .models import CustomUser, Parent
from .forms import ParentLoginForm, ParentSignUpForm
from .services import get_enrollments_from_parent, get_student_data_from_enrollment



def parent_login(request : HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("account:parent_account")
    form = ParentLoginForm(request.POST or None)
    if request.method == request.POST and form.is_valid:
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(request, email=email, password=password)
        login(request, user)
        
        return redirect("account:parent_account")
    else:
        return render(request, "account/parent_login.html", {})

def parent_sign_up(request : HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("account:parent_account")
    form = ParentSignUpForm(request.POST or None)
    if request.method == request.POST and form.is_valid():
        name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        role = CustomUser.Role.PARENT
        email = form.cleaned_data.get("email")
        phone_number = form.cleaned_data.get("phone_number")
        alternate_phone_number = form.cleaned_data.get("alternate_phone_number")
        adress = f"Commune de {form.cleaned_data.get("township")}, quartier {form.cleaned_data.get("quater")}, avenue / rue {form.cleaned_data.get("street")} numero {form.cleaned_data.get("street_number")}"
        password = form.cleaned_data.get("password")
        
        user = User.objects.create_user(f"{name} {last_name}", email, password, name=name, last_name=last_name, role=role)
        Parent.objects.create(user=user, phone_number=phone_number, alternate_phone_number=alternate_phone_number, adress=adress)
        login(request, user)
        
        return redirect("account:parent_account")
        
    else:
        return render(request, "account/sign_up.html", {})
    
@login_required
def parent_logout(request : HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("home:index")

@login_required
def parent_account(request : HttpRequest) -> HttpResponse:
    if request.user.__getattribute__("role") == CustomUser.Role.PARENT:
        parent = Parent.objects.get(user=request.user)
        
        if parent:
            data = {
                "student" : []
            }
            enrollments = get_enrollments_from_parent(parent)
            for enrollment in enrollments:
                data["student"].append(
                    get_student_data_from_enrollment(enrollment)
                )
            
            return render(request, "account/parent_account.html", data)
        else:
            return render(request, "account/bad_auth.html", {"error": "Aucun compte parent n'est associe a ce compte utilisateur"})