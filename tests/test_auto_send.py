from unittest.mock import Mock

import pytest

from pretix_attendance_certificate import checkin_handlers, tasks


@pytest.fixture
def apply_async(monkeypatch):
    apply_async = Mock()
    monkeypatch.setattr(
        tasks.send_automatic_certificate, "apply_async", apply_async
    )
    return apply_async


@pytest.mark.django_db
def test_auto_send_disabled_by_default(
    event, checkin, apply_async, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        checkin_handlers.on_checkin_created(sender=event, checkin=checkin)

    apply_async.assert_not_called()


@pytest.mark.django_db
def test_auto_send_enqueued_when_enabled(
    event, pos, checkin, apply_async, django_capture_on_commit_callbacks
):
    event.settings.attendance_certificate_auto_send = True

    with django_capture_on_commit_callbacks(execute=True):
        checkin_handlers.on_checkin_created(sender=event, checkin=checkin)

    apply_async.assert_called_once_with(
        kwargs={"event": event.pk, "position_id": pos.pk}
    )
