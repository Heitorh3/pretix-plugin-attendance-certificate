from django.utils.translation import gettext_lazy as _

DEFAULT_SUBJECT = _("[{event}] Seu certificado de participação")

DEFAULT_MESSAGE = _(
    "Hello,\n\n"
    "Your certificate of attendance for the event {event} "
    "is attached to this email.\n\n"
    "Best regards,\n"
    "Organizing Team"
)
