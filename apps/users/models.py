from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common import validators as common_validators
from apps.common.choices import UserRoleTypes
from apps.common.base_models import BaseModel


class User(AbstractUser, BaseModel):
    class Meta:
        db_table = "user"
        ordering = ["-date_joined"]
        verbose_name = _("user")
        verbose_name_plural = _("users")

    phone_number = models.CharField(
        verbose_name=_("phone number"),
        unique=True,
        error_messages={
            "unique": _("A user with that phone number already exists."),
        },
        max_length=100,
        validators=[common_validators.phone_number_validator]
    )
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
        null=True,
        blank=True
    )
    role = models.CharField(choices=UserRoleTypes.choices, default=UserRoleTypes.ORDINARY, max_length=50)

    profile_picture = models.ImageField(
        verbose_name=_("profile picture"),
        upload_to="profile_pictures/",
        null=True,
        blank=True,
    )

    EMAIL_FIELD = None
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        if self.is_deleted:
            return f"Deleted user: {self.phone_number.split('__')[1]}"
        return f"{self.pk}. {self.role} {self.phone_number}"

    # def generate_otp(self, typ=UserOTPTypes.OTHER, phone_number=None):
    #     from apps.common.utils import send_sms
    #     otp = self.user_otps.filter(
    #         is_deleted=False,
    #         is_confirmed=False,
    #         type=typ,
    #         phone_number=phone_number,
    #         created_at__gt=timezone.now() - timezone.timedelta(seconds=settings.OTP_EXPIRATION_TIME)
    #     ).first()
    #
    #     if otp:
    #         return otp
    #
    #     if self.phone_number == "+998000000000":
    #         code = "0000"
    #     elif self.phone_number == "+998111111111":
    #         code = "1111"
    #     else:
    #         code = user_utils.generate_otp()
    #
    #     otp = UserOTP.objects.create(user=self, type=typ, code=code, phone_number=phone_number)
    #     send_sms(otp)
    #     return otp
    #
    # @property
    # def account_settings(self):
    #     if hasattr(self, "_account_settings"):
    #         return self._account_settings
    #     return AccountSettings.objects.create(user_id=self.pk)
    #
    # def generate_refresh_token(self):
    #     from rest_framework_simplejwt.tokens import RefreshToken
    #     from rest_framework_simplejwt.settings import api_settings
    #     from django.contrib.auth.models import update_last_login
    #
    #     refresh = RefreshToken.for_user(self)
    #     data = dict()
    #     data["refresh"] = str(refresh)
    #     data["access"] = str(refresh.access_token)
    #
    #     if api_settings.UPDATE_LAST_LOGIN:
    #         update_last_login(None, self)
    #
    #     return data
    #
    # def delete_account(self):
    #     """
    #     change user phone number to: deleted__+998901234567__timestamp
    #     :return: None
    #     """
    #     self.is_active = False
    #     self.is_deleted = True
    #     self.deleted_at = timezone.now()
    #     self.phone_number = f"deleted__{self.phone_number}__{timezone.now().timestamp()}"
    #     self.save()
    #
    # def is_client(self):
    #     if hasattr(self, "client"):
    #         return True
