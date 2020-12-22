# Generated by Django 2.2.16 on 2020-10-10 14:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

import django_extensions.db.fields
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oauth', '0012_add_remote_id_and_vcs_provider_field'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE oauth_remoterepository_users RENAME TO oauth_remoterepositoryrelation',
                    reverse_sql='ALTER TABLE oauth_remoterepositoryrelation RENAME TO oauth_remoterepository_users',
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name='RemoteRepositoryRelation',
                    fields=[
                        (
                            'id',
                            models.AutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name='ID',
                            ),
                        ),
                        (
                            'user',
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name='remote_repository_relations',
                                to=settings.AUTH_USER_MODEL
                            ),
                        ),
                        (
                            'remote_repository',
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name='remote_repository_relations',
                                to='oauth.RemoteRepository'
                            ),
                        ),
                    ],
                ),
                migrations.AlterField(
                    model_name='remoterepository',
                    name='users',
                    field=models.ManyToManyField(
                        related_name='oauth_repositories',
                        through='oauth.RemoteRepositoryRelation',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Users'
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='remoterepositoryrelation',
            name='account',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='remote_repository_relations',
                to='socialaccount.SocialAccount',
                verbose_name='Connected account'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='remoterepositoryrelation',
            unique_together={('remote_repository', 'account')},
        ),
        migrations.AddField(
            model_name='remoterepositoryrelation',
            name='admin',
            field=models.BooleanField(
                default=False,
                verbose_name='Has admin privilege'
            ),
        ),
        migrations.AddField(
            model_name='remoterepositoryrelation',
            name='json',
            field=jsonfield.fields.JSONField(
                default=dict,
                verbose_name='Serialized API response'
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='remoterepositoryrelation',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='created',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='remoterepositoryrelation',
            name='modified',
            field=django_extensions.db.fields.ModificationDateTimeField(
                auto_now=True,
                verbose_name='modified'
            ),
        ),
    ]
