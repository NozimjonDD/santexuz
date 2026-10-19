"""Render a contract from its immutable text, parties, and quote snapshots."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from django.conf import settings
from rest_framework.exceptions import ValidationError
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def render_contract(contract):
    font_path = Path(settings.CONTRACT_FONT_PATH) if settings.CONTRACT_FONT_PATH else None
    if not font_path or not font_path.is_file():
        raise ValidationError({"pdf": "Configure CONTRACT_FONT_PATH with a Unicode TrueType font."})
    if "SantexUnicode" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("SantexUnicode", str(font_path)))
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=(210 * mm, 297 * mm),
                                 leftMargin=20 * mm, rightMargin=20 * mm,
                                 topMargin=18 * mm, bottomMargin=18 * mm)
    styles = getSampleStyleSheet()
    body = ParagraphStyle("ContractBody", parent=styles["BodyText"], fontName="SantexUnicode", fontSize=10, leading=15)
    title = ParagraphStyle("ContractTitle", parent=body, fontSize=16, leading=22, spaceAfter=12)
    labels = {
        "uz": ("Xizmat shartnomasi", "Taraflar", "Smeta", "Imzolar", "Jami", "Avans", "Mijoz", "Santexnik", "Do‘kon", "Xizmat markazi"),
        "ru": ("Договор оказания услуг", "Стороны", "Смета", "Подписи", "Итого", "Аванс", "Заказчик", "Мастер", "Магазин", "Сервисный центр"),
        "en": ("Service agreement", "Parties", "Estimate", "Signatures", "Total", "Advance", "Customer", "Plumber", "Store", "Service center"),
    }[contract.language]

    def paragraph(text):
        return Paragraph(escape(str(text)).replace("\n", "<br/>"), body)

    story = [Paragraph(f"{labels[0]} #{contract.order_id} / v{contract.quote.version}", title)]
    story += [paragraph(f"{contract.language} · template v{contract.template_version}"), Spacer(1, 5 * mm), paragraph(labels[1])]
    parties = contract.parties_snapshot
    for key, label in zip(("customer", "plumber", "store", "center"), labels[6:]):
        story.append(paragraph(f"{label}: {parties.get(key, '')}"))
    extra_labels = {
        "uz": ("Manzil", "Mijoz telefoni", "Taxminiy boshlanish", "Taxminiy tugash"),
        "ru": ("Адрес", "Телефон заказчика", "Планируемое начало", "Планируемое окончание"),
        "en": ("Address", "Customer phone", "Estimated start", "Estimated end"),
    }[contract.language]
    for key, label in zip(("address", "phone", "work_starts_at", "work_ends_at"), extra_labels):
        story.append(paragraph(f"{label}: {parties.get(key, '')}"))
    story += [Spacer(1, 5 * mm), paragraph(contract.text_snapshot), Spacer(1, 5 * mm), paragraph(labels[2])]
    snapshot = contract.quote.snapshot
    for section in ("services", "materials"):
        for item in snapshot.get(section, []):
            story.append(paragraph(f"{item.get('name', '')}: {item.get('quantity', '')} {item.get('unit', '')} × {item.get('unit_price', '')} UZS"))
    # Monetary breakdown is copied from the quote, never recalculated at rendering.
    money_labels = {
        "uz": ("Xizmatlar", "Materiallar", "Yetkazish", "Shoshilinch chaqiruv", "Platforma haqi"),
        "ru": ("Услуги", "Материалы", "Доставка", "Срочный вызов", "Плата платформе"),
        "en": ("Services", "Materials", "Delivery", "Urgent call", "Platform fee"),
    }[contract.language]
    for key, label in zip(("service_total", "material_total", "delivery_fee", "urgent_fee", "platform_fee"), money_labels):
        if key in snapshot:
            story.append(paragraph(f"{label}: {snapshot[key]} UZS"))
    story += [paragraph(f"{labels[4]}: {contract.quote.total} UZS"), paragraph(f"{labels[5]}: {contract.quote.advance_required} UZS"), Spacer(1, 8 * mm), paragraph(labels[3])]
    table = Table([[paragraph(label), paragraph("____________________")] for label in labels[6:]], colWidths=[85 * mm, 75 * mm])
    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 16), ("LINEBELOW", (0, -1), (-1, -1), 0.3, colors.grey)]))
    story.append(table)
    story.append(paragraph({"uz": "Huquqiy farqda o‘zbekcha matn ustuvor.", "ru": "При расхождениях приоритет имеет узбекский текст.", "en": "The Uzbek text prevails in case of legal differences."}[contract.language]))
    document.build(story)
    return output.getvalue()
