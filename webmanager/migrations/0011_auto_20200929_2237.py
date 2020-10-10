# Generated by Django 3.1 on 2020-09-29 22:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webmanager', '0010_connectedplace_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connectedplace',
            name='connected_place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connected_place', to='webmanager.place'),
        ),
    ]
