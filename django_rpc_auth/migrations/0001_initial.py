from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('session_key', models.CharField(max_length=40, primary_key=True, serialize=False,
                                                 verbose_name='Session key')),
                ('expire_date', models.DateTimeField(db_index=True, verbose_name='Expire date')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL,
                                           verbose_name='User')),
            ],
        ),
    ]
