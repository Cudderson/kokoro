# Generated by Django 3.1.7 on 2021-05-04 17:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kokoro_app', '0014_profilepost'),
    ]

    operations = [
        migrations.CreateModel(
            name='PinnedProfilePost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kokoro_app.profilepost')),
                ('pinned_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
