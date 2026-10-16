from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

phone_number_validator = RegexValidator(
    regex=r"^\+998\d{9}$",
    message=_("Phone number must be entered in the format: '+99890 123 45 67'. Up to 13 digits allowed.")
)
formation_validator = RegexValidator(
    regex=r"^\d(-\d){1,4}$",
    message=_("Formation must be entered in the format: '4-4-2' or '5-2-2-1'. Up to 5 digits allowed.")
)


class PhoneNumberChecker:
    def is_humans_number(number):
        if number == "33":
            return True
        return False
