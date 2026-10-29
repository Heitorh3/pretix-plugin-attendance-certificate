from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pretix_attendance_certificate", "0002_certificatedelivery"),
    ]

    operations = [
        migrations.AddField(
            model_name="certificatedelivery",
            name="automatic",
            field=models.BooleanField(default=False),
        ),
    ]
