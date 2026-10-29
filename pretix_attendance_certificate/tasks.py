import datetime

from django.db import transaction
from django.utils import timezone
from pretix.celery_app import app
from pretix.base.services.tasks import ProfiledEventTask
from pretix.base.models import (
    Event,
    InvoiceAddress,
    OrderPosition,
    User,
    CachedFile,
)
from i18nfield.strings import LazyI18nString
from pretix.base.services.mail import mail
from pretix.base.i18n import language
from pretix.helpers.format import format_map
from pretix.base.email import get_email_context
from pretix_attendance_certificate.render import render_certificate
from pretix_attendance_certificate.models import CertificateDelivery

import logging

logger = logging.getLogger(__name__)


@app.task(base=ProfiledEventTask, acks_late=True)
def send_certificate_of_attendance_mails(
    event: Event,
    user: int,
    subject: dict,
    message: dict,
    objects: list,
):
    user = User.objects.get(pk=user) if user else None

    subject = LazyI18nString(subject)
    message = LazyI18nString(message)

    positions = OrderPosition.objects.filter(
        pk__in=objects,
        order__event=event,
    ).select_related("order")

    for position in positions:
        order = position.order

        # Prioriza o e-mail individual do participante.
        # Se estiver vazio, utiliza o e-mail do pedido.
        recipient = (position.attendee_email or "").strip() or (
            order.email or ""
        ).strip()

        if not recipient:
            order.log_action(
                "pretix_attendance_certificate.skipped.no_email",
                user=user,
                data={"position": position.positionid},
            )
            continue

        with transaction.atomic():
            (
                delivery,
                created,
            ) = CertificateDelivery.objects.select_for_update().get_or_create(
                position=position,
                defaults={
                    "status": CertificateDelivery.STATUS_SENDING,
                    "recipient": recipient,
                },
            )
            if not created:
                delivery.status = CertificateDelivery.STATUS_SENDING
                delivery.recipient = recipient
                delivery.sent_at = None
                delivery.error = ""
                delivery.save(
                    update_fields=[
                        "status",
                        "recipient",
                        "sent_at",
                        "error",
                        "updated",
                    ]
                )

        try:
            try:
                invoice_address = order.invoice_address
            except InvoiceAddress.DoesNotExist:
                invoice_address = InvoiceAddress(order=order)

            with language(order.locale, event.settings.region):
                email_context = get_email_context(
                    event=event,
                    order=order,
                    position=position,
                    invoice_address=invoice_address,
                )

                rendered_certificate = render_certificate(
                    position=position,
                    event=event,
                )

                cache_file = CachedFile.objects.create(
                    filename="certificate_of_attendance.pdf",
                    expires=timezone.now() + datetime.timedelta(days=7),
                    file=rendered_certificate,
                )

                mail(
                    recipient,
                    subject,
                    message,
                    email_context,
                    event,
                    locale=order.locale,
                    order=order,
                    position=position,
                    attach_tickets=False,
                    attach_cached_files=[cache_file],
                )
        except Exception as exc:
            # Record the failure and keep going, so one broken position does
            # not stop the remaining attendees of a bulk send.
            logger.exception(
                "Could not send certificate of attendance for position %s",
                position.pk,
            )
            delivery.status = CertificateDelivery.STATUS_FAILED
            delivery.error = str(exc)[:1000]
            delivery.save(update_fields=["status", "error", "updated"])
            order.log_action(
                "pretix_attendance_certificate.failed.attendee",
                user=user,
                data={
                    "position": position.positionid,
                    "recipient": recipient,
                    "error": delivery.error,
                },
            )
            continue

        delivery.status = CertificateDelivery.STATUS_SENT
        delivery.sent_at = timezone.now()
        delivery.error = ""
        delivery.save(update_fields=["status", "sent_at", "error", "updated"])
        order.log_action(
            "pretix_attendance_certificate.sent.attendee",
            user=user,
            data={
                "position": position.positionid,
                "subject": format_map(
                    subject.localize(order.locale),
                    email_context,
                ),
                "message": format_map(
                    message.localize(order.locale),
                    email_context,
                ),
                "recipient": recipient,
            },
        )
