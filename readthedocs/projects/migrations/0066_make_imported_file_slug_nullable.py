# Generated by Django 2.2.12 on 2020-06-24 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0065_add_feature_future_default_true'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importedfile',
            name='slug',
            field=models.SlugField(null=True, verbose_name='Slug'),
        ),
    ]
