# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1024)),
                ('faculty_group', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='faculty_of', blank=True, to='auth.Group', null=True)),
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b"type of data. Useful ones are 'instructor', 'semester', 'url', 'campus', 'times', 'call_number'", max_length=64)),
                ('value', models.CharField(help_text=b"The name's value for the course.", max_length=1024)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courseaffils.Course')),
            ],
            options={
                'verbose_name_plural': 'Course Details',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(null=True, blank=True)),
                ('term', models.IntegerField(blank=True, null=True, choices=[(1, b'Spring'), (2, b'Summer'), (3, b'Fall')])),
                ('starttime', models.TimeField(null=True, blank=True)),
                ('endtime', models.TimeField(null=True, blank=True)),
                ('days', models.CharField(max_length=7, null=True, blank=True)),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='info', to='courseaffils.Course')),
            ],
            options={
                'verbose_name_plural': 'Course Info',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('custom_headers', models.TextField(help_text=b'Replaces main.css link in header.  You need to add this as full HTML (&lt;link rel="stylesheet" href="...." />) but the advantage is you can add custom javascript here, too.', null=True, blank=True)),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='courseaffils.Course')),
            ],
            options={
                'verbose_name_plural': 'Course Settings',
            },
            bases=(models.Model,),
        ),
    ]
