import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_settings_page_saves_mail_texts(settings_client, event):
    url = reverse(
        "plugins:pretix_attendance_certificate:settings",
        kwargs={"organizer": event.organizer.slug, "event": event.slug},
    )
    assert settings_client.get(url).status_code == 200

    response = settings_client.post(
        url,
        {
            "attendance_certificate_mail_subject_0": "Seu certificado",
            "attendance_certificate_mail_text_0": "Olá {event}",
        },
    )

    assert response.status_code == 302
    event.settings.flush()
    assert str(event.settings.attendance_certificate_mail_subject) == (
        "Seu certificado"
    )
