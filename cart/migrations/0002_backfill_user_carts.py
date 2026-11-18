from django.conf import settings
from django.db import migrations


def backfill_carts(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    Cart = apps.get_model("cart", "Cart")
    database = schema_editor.connection.alias

    user_ids = User.objects.using(database).values_list("pk", flat=True)
    for user_id in user_ids.iterator():
        Cart.objects.using(database).get_or_create(user_id=user_id)


class Migration(migrations.Migration):
    dependencies = [("cart", "0001_initial")]

    operations = [
        migrations.RunPython(backfill_carts, migrations.RunPython.noop),
    ]
