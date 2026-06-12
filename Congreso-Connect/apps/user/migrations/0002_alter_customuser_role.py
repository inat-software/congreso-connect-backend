from django.db import migrations, models


class Migration(migrations.Migration):
    """Agrega el rol 'registrador' a las opciones del campo role.

    Es solo un cambio de `choices` (no altera el esquema de la columna en
    Postgres), pero se versiona para mantener el estado de migraciones limpio.
    """

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin', 'Administrador'),
                    ('expositor', 'Expositor'),
                    ('registrador', 'Registrador'),
                    ('user', 'Usuario'),
                ],
                db_index=True,
                default='user',
                max_length=20,
                verbose_name='rol',
            ),
        ),
    ]
