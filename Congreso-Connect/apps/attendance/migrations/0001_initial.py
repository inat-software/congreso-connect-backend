import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(max_length=150, verbose_name='nombres')),
                ('last_name', models.CharField(max_length=150, verbose_name='apellidos')),
                ('dni', models.CharField(blank=True, max_length=20, verbose_name='DNI')),
                ('method', models.CharField(choices=[('qr', 'Escaneo de QR'), ('manual', 'Ingreso manual')], db_index=True, default='manual', max_length=10, verbose_name='metodo')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendance', to=settings.AUTH_USER_MODEL, verbose_name='usuario')),
                ('registered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registered_attendances', to=settings.AUTH_USER_MODEL, verbose_name='registrado por')),
            ],
            options={
                'verbose_name': 'Asistencia',
                'verbose_name_plural': 'Asistencias',
                'db_table': 'attendance_attendance',
                'ordering': ['-created_at'],
            },
        ),
    ]
