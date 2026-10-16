from django.db import models

from django.utils.translation import gettext_lazy as _
from apps.common.base_models import BaseModel


class Region(BaseModel):
    class Meta:
        db_table = "region"
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")

    name = models.CharField(max_length=255, default="region")
    name_en = models.CharField(max_length=255, default="region")
    name_uz = models.CharField(max_length=255, default="region")
    name_ru = models.CharField(max_length=255, default="region")
    post_code = models.CharField(max_length=10, default=0)
    soato = models.CharField(max_length=20, verbose_name=_("soato"), default=1, unique=True)

    def __str__(self):
        return f"{self.name_uz}"


class District(BaseModel):
    class Meta:
        db_table = "district"
        verbose_name = _("District")
        verbose_name_plural = _("Districts")

    name = models.CharField(max_length=255, default="Name", verbose_name=_("Name"))
    name_uz = models.CharField(max_length=255, default="Name",  verbose_name=_("Name"))
    name_en = models.CharField(max_length=255, default="Name",  verbose_name=_("Name"))
    name_ru = models.CharField(max_length=255, default="Name",  verbose_name=_("Name"))
    region = models.ForeignKey(
        to="Region", verbose_name=_("Region"), on_delete=models.CASCADE, related_name="districts"
    )
    soato = models.CharField(max_length=20, verbose_name=_("soato"), default=1, unique=True)

    def __str__(self):
        return f"{self.name_uz}"
