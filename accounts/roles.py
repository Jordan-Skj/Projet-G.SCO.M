from django.contrib.auth.models import Group, Permission

from .models import CustomUser

def crud(app: str, model: str, actions: tuple[str, ...]) -> tuple[str, ...]:
    """Build permission names"""
    return tuple(f"{app}.{action}_{model}" for action in actions)

VIEW_BOTH: tuple[str, ...] = ("view",)
"""Permission to view primary and secondary education informations"""
VIEW_PRIMARY: tuple[str, ...] = ("view_primary_only")
"""Permission to view only primary education informations"""
VIEW_SECONDARY: tuple[str, ...] = ("view_secondary_only")
"""Permission to view  only secondary education informations"""

MANAGE_BOTH: tuple[str, ...] = ("view", "add", "change")
"""Permission to add and edit primary and secondary education informations"""
MANAGE_PRIMARY: tuple[str, ...] = ("view_primary_only", "add_primary_only", "change_primary_only")
"""Permission to add and edit only primary education informations"""
MANAGE_SECONDARY: tuple[str, ...] = ("view_secondary_only", "add_secondary_only", "change_secondary_only")


BASIC_ACADEMIC_VIEW: tuple[str, ...] = (
    *crud("students", "student", VIEW_BOTH),
    *crud("students", "enrollement", VIEW_BOTH),
    *crud("students", "schoolclass", VIEW_BOTH),
    *crud("students", "academicyear", VIEW_BOTH),
)

SECONDARY_ACADEMIC_VIEW: tuple[str, ...] = [
    *crud("students", "student", VIEW_SECONDARY),
    *crud("students", "enrollement", VIEW_SECONDARY),
    *crud("students", "schoolclass", VIEW_SECONDARY),
    *crud("students", "academicyear", VIEW_SECONDARY),
]


ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    CustomUser.Role.DISCIPLINE_DIRECTOR: (
        *BASIC_ACADEMIC_VIEW,
        *crud("students", "studentguardian", VIEW_BOTH),
        *crud("accounts", "parent", VIEW_BOTH),
        *crud("finance", "fee", VIEW_BOTH),
        *crud("finance", "feepayment", VIEW_BOTH),
        *crud("discipline", "punishment", MANAGE_BOTH),
        *crud("audit", "auditlog", VIEW_BOTH),
        "finance.verify_feepayment",
        "discipline.authorize_return_to_class",
    ),
    CustomUser.Role.HEADMASTER: (
        *crud("students", "student", MANAGE_BOTH),
        *crud("students", "enrollment", MANAGE_BOTH),
        *crud("students", "studentguardian", MANAGE_BOTH),
        *crud("students", "schoolclass", MANAGE_BOTH),
        *crud("students", "academicyear", VIEW_BOTH),
        *crud("accounts", "parent", MANAGE_BOTH),
        *crud("finance", "fee", MANAGE_BOTH),
    ),
    CustomUser.Role.TEACHER: SECONDARY_ACADEMIC_VIEW,
    CustomUser.Role.CLASSTEACHER: (),
    CustomUser.Role.ACCOUNTANT: (
        *BASIC_ACADEMIC_VIEW,
        *crud("finance", "fee", MANAGE_BOTH),
        *crud("finance", "feepayment", MANAGE_BOTH),
        "finance.verify_feepayment",
        "finance.void_feepayment",
    ),
    CustomUser.Role.PARENT: (),
    CustomUser.Role.GUARD: ("discipline.check_class_access",),
    CustomUser.Role.PRIMARY_HEADMASTER: (
        *crud("students", "student", MANAGE_PRIMARY),
        *crud("students", "enrollment", MANAGE_PRIMARY),
        *crud("students", "studentguardian", MANAGE_PRIMARY),
        *crud("students", "schoolclass", MANAGE_PRIMARY),
        *crud("students", "academicyear", VIEW_PRIMARY),
        *crud("accounts", "parent", MANAGE_PRIMARY),
        *crud("finance", "fee", MANAGE_PRIMARY),
        "discipline.authorize_return_to_class",
    ),
    CustomUser.Role.INSPECTOR: (
        *BASIC_ACADEMIC_VIEW,
        *crud("discipline", "punishment", VIEW_BOTH),
    ),
    CustomUser.Role.ADMIN: (
        *crud("accounts", "customuser", MANAGE_BOTH),
        *crud("accounts", "parent", MANAGE_BOTH),
    ),
}

def get_permission(full_name: str) -> Permission:
    app_label, codename = full_name.split(".", maxsplit=1)
    return Permission.objects.get(content_type__app_label=app_label, codename=codename)

def sync_user_group(user: CustomUser) -> None:
    """Put the user in the group matching their role, and in no other role group."""
    wanted_group, _ = Group.objects.get_or_create(name=user.role)
    other_groups = Group.objects.filter(name__in=[role.value for role in CustomUser.Role]).exclude(pk=wanted_group.pk)
    user.groups.remove(*other_groups)
    user.groups.add(wanted_group)