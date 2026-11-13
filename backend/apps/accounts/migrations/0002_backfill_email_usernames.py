import re

from django.conf import settings
from django.db import migrations


def backfill_email_usernames(apps, schema_editor):
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    user_model = apps.get_model(app_label, model_name)
    database = schema_editor.connection.alias

    for user in user_model.objects.using(database).exclude(email="").iterator():
        if not re.fullmatch(r"[0-9a-f]{32}", user.username):
            continue

        base = user.email.partition("@")[0][:150]
        username = base
        suffix = 2
        while user_model.objects.using(database).filter(
            username__iexact=username
        ).exclude(pk=user.pk).exists():
            username = f"{base[: 150 - len(str(suffix))]}{suffix}"
            suffix += 1

        user_model.objects.using(database).filter(pk=user.pk).update(username=username)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(backfill_email_usernames, migrations.RunPython.noop),
    ]
