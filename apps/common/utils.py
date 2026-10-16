import json
import re

import requests
import requests.auth
from django.conf import settings

from apps.common import models
from .choices import UserOTPTypes

# SMS_TEMPLATE for OTP messages
SMS_TEMPLATE = {
    UserOTPTypes.LOGIN.value: "Kod verifikasii dlya vxoda: %s",
    UserOTPTypes.REGISTER.value: "Kod verifikasii dlya vxoda: %s",
    UserOTPTypes.RESET_PASSWORD.value: "Profan.uz mobil ilovasida parolni qayta tiklash uchun tasdiqlash kodi: %s. Kodni hech kimga bermang!",
    UserOTPTypes.DELETE_ACCOUNT.value: "Profan.uz mobil ilovasida telefon raqamini o’zgartirish uchun tasdiqlash kodi: %s. Kodni hech kimga bermang!",
    UserOTPTypes.CHANGE_PHONE_NUMBER.value: "Profan.uz mobil ilovasida hisobni o’chirish uchun tasdiqlash kodi: %s. Kodni hech kimga bermang!",
    UserOTPTypes.OTHER.value: "",
}


def sms_notification(instance, request_type):
    import datetime
    date_time = datetime.datetime.now()
    if request_type == 'new_order':
        date_time = instance.time
    SMS_NOTIFICATION = {
        "new_request": "Vasha zayavka na konsultatsyu uspeshno poluchena! Spetsialist skoro svyajetsa s vami. Poka "
                       "jdete, vi mojete voyti v svoy akkaunt: https://domain.uz/profile",

        "new_order": f"Spetsialist sozdal zakaz dlya vas na {date_time.strftime('%d %B, %Y')} goda v {date_time.strftime('%H:%M')}. "
                     f"Pojaluysta, voydite v svoy akkaunt dlya detaley: https://domain.uz/profile"
    }

    return SMS_NOTIFICATION[request_type]


def pretty_price(price):
    if price >= 1_000_000:
        pretty_value = f'{price / 1_000_000:.1f}mln'
    elif price >= 1_000:
        pretty_value = f'{price / 1_000:.1f}k'
    else:
        pretty_value = str(price)

    return pretty_value.rstrip('0').rstrip('.') if '.' in pretty_value else pretty_value


def clean_html(html):
    # Remove HTML tags, nbsp; and &amp;
    clean_text = re.sub(pattern=r'<[^>]*?>', repl='', string=html)
    clean_text = re.sub(pattern=r'&nbsp;', repl=' ', string=clean_text)
    clean_text = re.sub(pattern=r'&amp;', repl='&', string=clean_text)
    return clean_text


# Playmobile
def send_sms(otp):
    if settings.SMS_DEBUG:
        return None

    url = "https://send.smsxabar.uz/broker-api/send"
    recipient = otp.user.phone_number[1:]
    data = {
        "messages": [
            {
                "recipient": recipient,
                "message-id": str(otp.id),
                "sms": {
                    "originator": "3700",
                    "content": {
                        "text": SMS_TEMPLATE[otp.type] % otp.code
                    }
                }
            }
        ]
    }
    try:
        response = requests.post(
            url=url,
            auth=requests.auth.HTTPBasicAuth(settings.SMS_USERNAME, settings.SMS_PASSWORD),
            json=data
        )
    except (requests.ConnectionError, requests.Timeout):
        return False

    if response.status_code == 200:
        return True
    return False


def send_notify_sms(instance, request_type):
    if settings.SMS_DEBUG:
        return None
    url = "https://send.smsxabar.uz/broker-api/send"

    recipient = instance.client.user.phone_number[1:]
    data = {
        "messages": [
            {
                "recipient": recipient,
                "message-id": str(instance.id),
                "sms": {
                    "originator": "3700",
                    "content": {
                        "text": sms_notification(instance, request_type)
                    }
                }
            }
        ]
    }
    try:
        response = requests.post(
            url=url,
            auth=requests.auth.HTTPBasicAuth(settings.SMS_USERNAME, settings.SMS_PASSWORD),
            json=data
        )
    except (requests.ConnectionError, requests.Timeout):
        return False

    if response.status_code == 200:
        return True
    return False


def update_regions():
    file_name = "apps/common/management/data/regions.json"
    with open(file_name, "r") as file:
        regions = json.load(file)

        for region in regions:
            models.Region.objects.update_or_create(
                soato=region["soato"],
                defaults={
                    "name_uz": region["name"],
                    "name_ru": region["name_ru"],
                    "name_en": region["name_en"],
                }
            )


def update_districts():
    file_name = "apps/common/management/data/districts.json"

    with open(file_name, "r") as file:
        districts = json.load(file)

        for district in districts:
            models.District.objects.update_or_create(
                soato=district["soato"],
                defaults={
                    "name_uz": district["name"],
                    "name_ru": district["name_ru"],
                    "name_en": district["name_en"],
                    "region": models.Region.objects.get(soato=str(district["soato"])[:4]),
                }
            )
