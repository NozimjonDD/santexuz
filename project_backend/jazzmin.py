JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Gossip Girl Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Gossip Girl",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Gossip Girl",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "images/logo.png",

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": "images/logo.png",

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": None,

    # CSS classes that are applied to the logo above
    "site_logo_classes": "",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": "images/logo.png",

    # Welcome text on the login screen
    "welcome_sign": "Welcome to the Boto Clinic Admin",

    # Copyright on the footer
    "copyright": "Gossip Girl",

    # List of model admins to search from the search bar, search bar omitted if excluded
    # If you want to use a single search field you dont need to use a list, you can use a simple string
    # "search_model": ["auth.User", "auth.Group"],

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": "profile_picture",

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [

        # model admin to link to (Permissions checked against model)
        {"model": "user.User"},

        # App with dropdown menu to all its models pages (Permissions checked against models)
        # {"app": "books"},
    ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        # {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": False,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": [

        "users",
        "users.User",
        "users.Device",
        "users.GroupProxyModel",
        "users.UserOTP",
        "users.UserAddress",
        "users.UserComment",

        "common",
        "common.Settings",
        "common.Category",
        "common.Banner",
        "common.Region",
        "common.District",
        "common.Language",
        "common.LanguageLevel",
        "common.WeekDay",

        "client",
        "client.Client",
        "client.Consultation",
        "client.Appointment",
        "client.AppointmentSession",

        "business",
        "business.Service",
        "business.ServiceTariff",
        "business.ServiceTariffType",
        "business.ServiceImage",
        "business.Specialist",
        "business.Specialty",
        "business.Education",
        "business.Experience",
        "business.SpecialistLanguage",
        "business.Certificate",
        "business.WorkingDay",

        "notification",
        "notification.Notification",
        "notification.UserNotification",
        "notification.NotificationType",
        "notification.NotificationTemplate",
    ],

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "users": "fas fa-users-cog",
        "users.User": "fas fa-user",
        "users.Device": "fas fa-mobile-alt",
        "users.GroupProxyModel": "fas fa-users",
        "users.UserOTP": "fas fa-key",
        "users.UserAddress": "fas fa-map-marker-alt",
        "users.UserComment": "fas fa-comment",

        "common": "fas fa-cogs",
        "common.Settings": "fas fa-cogs",
        "common.Category": "fas fa-list",
        "common.Banner": "fas fa-image",
        "common.Region": "fas fa-globe",
        "common.District": "fas fa-map-marker-alt",
        "common.Language": "fas fa-language",
        "common.LanguageLevel": "fas fa-list",
        "common.WeekDay": "fas fa-list",

        "client": "fas fa-users",
        "client.Client": "fas fa-user",
        "client.Consultation": "fas fa-comments",
        "client.Appointment": "fas fa-calendar-alt",
        "client.AppointmentSession": "fas fa-calendar-alt",

        "business": "fas fa-briefcase",
        "business.Service": "fas fa-heartbeat",
        "business.ServiceTariff": "fas fa-list",
        "business.ServiceTariffType": "fas fa-list",
        "business.ServiceImage": "fas fa-image",
        "business.Specialist": "fas fa-user-tie",
        "business.Specialty": "fas fa-award",
        "business.Education": "fas fa-graduation-cap",
        "business.Experience": "fas fa-clipboard-list",
        "business.SpecialistLanguage": "fas fa-language",
        "business.Certificate": "fas fa-certificate",
        "business.WorkingDay": "fas fa-calendar-alt",

        "notification": "fas fa-bell",
        "notification.Notification": "fas fa-bell",
        "notification.NotificationType": "fas fa-list",
        "notification.NotificationTemplate": "fas fa-list",
        "notification.UserNotification": "fas fa-bell",

        "auditlog": "fas fa-clipboard-list",
        "auditlog.LogEntry": "fas fa-clipboard-list",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": "css/custom_jazzmin.css",
    "custom_js": None,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    # Add a language dropdown into the admin
    "language_chooser": True,
}
