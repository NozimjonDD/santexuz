from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRoleTypes(models.TextChoices):
    ORDINARY = "ordinary", "Ordinary",
    BUSINESS = "business", "Business",
    HYBRID = "hybrid", "Hybrid",
    ADMIN = "admin", 'Admin',


class UserOTPTypes(models.TextChoices):
    LOGIN = "login", _("Login"),
    REGISTER = "register", _("Register"),
    RESET_PASSWORD = "reset_password", _("Reset password"),
    DELETE_ACCOUNT = "delete_account", _("Delete account"),
    CHANGE_PHONE_NUMBER = "change_phone_number", _("Change phone number"),
    OTHER = "other", "Other",


class CommentStatusTypes(models.TextChoices):
    PENDING = "pending", _("Pending")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")


class CurrencyTypes(models.TextChoices):
    UZS = "uzs", _("UZS")
    USD = "usd", _("USD")


class DateChoices(models.TextChoices):
    MIN = "min", _("Min")
    HOUR = "hour", _("Hour")
    DAY = "day", _("Day")
    WEEK = "week", _("Week")
    MONTH = "month", _("Month")
    YEAR = "year", _("Year")


class ServiceStatusTypes(models.TextChoices):
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")


class SpecialistStatusTypes(models.TextChoices):
    PENDING = "pending", _("Pending")
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    SUSPENDED = "suspended", _("Suspended")


class ModerationStatusChoices(models.TextChoices):
    PENDING = "pending", _("Pending")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")
    CANCELED = "canceled", _("Canceled")


class ModerationActionTypes(models.TextChoices):
    CREATE = "create", _("Create")
    UPDATE = "update", _("Update")
    DELETE = "delete", _("Delete")


class ConsultStatusTypes(models.TextChoices):
    PENDING = "pending", _("Pending")
    ACCEPTED = "accepted", _("Accepted")
    FINISHED = "finished", _("Finished")


class AppointmentStatusTypes(models.TextChoices):
    NOT_STARTED = "not_started", _("Not Started")
    IN_PROGRESS = "in_progress", _("In Progress")
    FINISHED = "finished", _("Finished")
    CANCELED = "canceled", _("Canceled")


class ReceptionTypes(models.TextChoices):
    HOME = "home", _("Home")
    OFFICE = "office", _("Office")


class AppointmentRequestStatus(models.TextChoices):
    NEW = "new", _("New")
    MODERATION_PENDING = "moderation_pending", _("Moderation Pending")
    MODERATION_REJECTED = "moderation_rejected", _("Moderation Rejected")
    PENDING = "pending", _("Pending")
    ACCEPTED = "accepted", _("Accepted")
    REJECTED = "rejected", _("Rejected")
    CANCELLED = "cancelled", _("Cancelled")


class EducationTypes(models.TextChoices):
    SCHOOL = "school", _("School")
    COLLEGE = "college", _("College")
    BACHELOR = "bachelor", _("Bachelor")
    MASTER = "master", _("Master")
    DOCTORATE = "doctorate", _("Doctorate")
    OTHER = "other", _("Other")


class ExperienceTypes(models.TextChoices):
    INTERN = "intern", _("Intern")
    PART_TIME = "part_time", _("Part Time")
    FULL_TIME = "full_time", _("Full Time")
    REMOTE = "remote", _("Remote")
    CONTRACT = "contract", _("Contract")
    OTHER = "other", _("Other")


class CertificateTypes(models.TextChoices):
    CERTIFICATE = "certificate", _("Certificate")
    LICENSE = "license", _("License")


class BeforeAfterMediaTypes(models.TextChoices):
    IMAGE = "image", _("Image")
    VIDEO = "video", _("Video")


class NotificationTypeChoices(models.TextChoices):
    INFORMATIONAL = "INFORMATIONAL", _("Informational")
    USER_ENGAGEMENT = "USER_ENGAGEMENT", _("User Engagement")
    TRANSACTIONAL = "TRANSACTIONAL", _("Transactional")
    PROMOTIONAL = "PROMOTIONAL", _("Promotional")


class NotificationDetailedEventTypes(models.TextChoices):
    APP_VERSION_UPDATED = "APP_VERSION_UPDATED", _("App version updated")
    NEWS_PUBLISHED = "NEWS_PUBLISHED", _("News published")
    NEW_APPOINTMENT_REQUEST = "NEW_APPOINTMENT_REQUEST", _("New appointment request")
    UPDATE_MODERATION_SENT = "UPDATE_MODERATION_SENT", _("Update Moderation Sent")
    UPDATE_MODERATION_APPROVED = "UPDATE_MODERATION_APPROVED", _("Update Moderation Approved")
    UPDATE_MODERATION_REJECTED = "UPDATE_MODERATION_REJECTED", _("Update Moderation Rejected")


# CHANGE LOG
class SourceTypes(models.TextChoices):
    SERVER = "server", _("Server")
    CLIENT = "client", _("Client")


class ChLModelTypes(models.TextChoices):
    APPOINTMENT_REQUEST = "appointment_request", _("Appointment Request")
    APPOINTMENT = "appointment", _("Appointment")


class ChLChangeTypes(models.TextChoices):
    CREATE = "create", _("Create")
    UPDATE = "update", _("Update")
    DELETE = "delete", _("Delete")
