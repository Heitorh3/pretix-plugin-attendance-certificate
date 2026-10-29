# pretix-plugin-attendance-certificate

A [pretix](https://pretix.eu) plugin to design certificates of attendance and
send them to attendees by email.

Used by [PyCon Italia](https://pycon.it).

## Features

- **Certificate editor:** design the certificate in the pretix PDF editor,
  with your own background PDF and attendee and event fields.
- **Bulk sending:** send the certificate to all attendees with a paid
  admission ticket from the pretix "Send out emails" page.
- **Per-attendee actions:** download or email the certificate from the order
  page.

## Installation

Install the plugin in the Python environment of your pretix installation:

```bash
pip install pretix-plugin-attendance-certificate
```

Apply the database migrations and restart pretix (web server and Celery
workers):

```bash
python -m pretix migrate
```

Then enable **Attendance Certificate** in the event under
*Settings → Plugins*.

## Usage

Once the plugin is enabled, the event menu shows a **Certificate of
Attendance** section with these pages:

| Page | What it does |
| --- | --- |
| Editor | Design the certificate layout and upload a background PDF. |
| Send out certificates | Email the certificate to all attendees with a paid admission ticket. |
| Settings | Edit the email text. |

### Designing the certificate

Open *Certificate of Attendance → Editor*. Upload a background PDF and place
fields such as the attendee name on it. To check the result, use the
**Certificate of attendance** button next to a ticket on any order page, which
downloads the PDF for that attendee.

### Sending certificates manually

- **To everyone:** *Certificate of Attendance → Send out certificates* uses
  the pretix email form, so you can write the subject and message and use the
  usual email placeholders.
- **To one attendee:** on the order page, click **Email certificate of
  attendance** next to the ticket. This button is shown only when the ticket
  has an attendee email.

### Email text

*Certificate of Attendance → Settings* (also listed under the event
*Settings* menu) has the **email subject** and **email text**, with one
field for each language of the event. Placeholders such as `{event}` are
replaced. These texts are used for the button on the order page. The default
text is in English.

### Permissions

| Action | Required permission |
| --- | --- |
| Download certificates | View orders |
| Email a certificate from the order page | Change orders |
| Change the plugin settings | Change event settings |

## Development

The plugin is developed and tested against **pretix 2026.8**. Create a
virtual environment, then install pretix, the test tools and the plugin in
editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
pip install "pretix==2026.8.0" pytest pytest-django
pip install -e .
```

Run the tests:

```bash
pytest
```

Tests use pretix's test settings (`pretix.testutils.settings`, configured in
`setup.cfg`) with a SQLite database. No extra services are needed.

To work on the plugin in a real pretix instance, install it in editable mode
in that instance's environment, run `python -m pretix migrate` and restart
the web server and the Celery workers.

### Project layout

```text
pretix_attendance_certificate/
├── apps.py               # plugin metadata and signal registration
├── email_defaults.py     # default email texts and plugin settings
├── models.py             # certificate layout
├── render.py             # renders the certificate PDF
├── signals.py            # menu entries, order page buttons, log messages
├── tasks.py              # Celery tasks that send the certificates
├── urls.py
├── views/
│   ├── editor.py         # certificate layout editor
│   ├── emails.py         # bulk sending page
│   ├── positions.py      # download / email a single certificate
│   └── settings.py       # plugin settings page
└── templates/
```

## License

MIT, see [LICENSE](LICENSE).
