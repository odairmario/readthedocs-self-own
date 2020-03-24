# Generated by Django 2.2.11 on 2020-03-24 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builds', '0014_migrate-doctype-from-project-to-version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='build',
            name='state',
            field=models.CharField(choices=[('triggered', 'Triggered'), ('cloning', 'Cloning'), ('installing', 'Installing'), ('building', 'Building'), ('uploading', 'Uploading'), ('finished', 'Finished')], default='finished', max_length=55, verbose_name='State'),
        ),
    ]
