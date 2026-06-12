from django.db import migrations


class Migration(migrations.Migration):
    """
    Limpia la columna huerfana `logo_url` de content_sponsor.

    `logo_url` existe fisicamente en algunas BD (local/server) por una cadena de
    migraciones vieja que ya no esta en git, pero el estado actual de Django no la
    conoce (el 0001 no la define). Por eso NO se puede usar RemoveField: se dropea
    a nivel de BD con `IF EXISTS`, que es idempotente: la elimina donde exista y no
    hace nada en una BD que nunca la tuvo. Asi local, server y BD nuevas convergen.
    """

    dependencies = [
        ('content', '0002_remove_sponsor_tier_remove_sponsor_website_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE content_sponsor DROP COLUMN IF EXISTS logo_url;',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
