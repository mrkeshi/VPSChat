from django.conf import settings

def site_settings(request):
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "Chat"),
        "ENABLE_FILE_UPLOAD": getattr(settings, "ENABLE_FILE_UPLOAD", True),
    }
