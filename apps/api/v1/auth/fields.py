from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from apps.common import validators as common_validators


class PhoneNumberField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs["max_length"] = 13
        # kwargs["min_length"] = 13
        kwargs["validators"] = [common_validators.phone_number_validator]
        super().__init__(**kwargs)


class PasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs["write_only"] = True
        kwargs["style"] = {"input_type": "password"}
        kwargs["min_length"] = 8
        kwargs["max_length"] = 64
        kwargs["validators"] = [validate_password]
        super().__init__(**kwargs)
