# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseaffils', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseinfo',
            name='days',
            field=models.CharField(
                help_text=b'e.g. "MTWRF"', max_length=7,
                null=True, blank=True),
        ),
    ]
