# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courseaffils', '0002_auto_20160316_1223'),
    ]

    operations = [
        migrations.CreateModel(
            name='Affil',
            fields=[
                ('id',
                 models.AutoField(
                     verbose_name='ID',
                     serialize=False,
                     auto_created=True,
                     primary_key=True)),
                ('activated', models.BooleanField(default=False)),
                ('name', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='affil',
            unique_together=set([('name', 'user')]),
        ),
    ]
