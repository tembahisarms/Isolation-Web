# Generated by Django 3.1 on 2020-08-24 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webmanager', '0008_place_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='member_count',
            field=models.IntegerField(default=True),
        ),
    ]
