"""Read the Docs tasks."""

from __future__ import division, print_function, unicode_literals

import os

from invoke import task, Collection

import common.tasks
import dockerfiles.tasks


ROOT_PATH = os.path.dirname(__file__)


namespace = Collection()
namespace.add_collection(
    Collection(
        common.tasks.prepare,
        common.tasks.release,
    ),
    name='deploy',
)

namespace.add_collection(
    Collection(
        common.tasks.setup_labels,
    ),
    name='github',
)

namespace.add_collection(
    Collection(
        common.tasks.upgrade_all_packages,
    ),
    name='packages',
)

namespace.add_collection(
    Collection(
        dockerfiles.tasks.build,
        dockerfiles.tasks.down,
        dockerfiles.tasks.up,
        dockerfiles.tasks.shell,
        dockerfiles.tasks.manage,
        dockerfiles.tasks.attach,
        dockerfiles.tasks.restart,
        dockerfiles.tasks.pull,
        dockerfiles.tasks.test,
    ),
    name='docker',
)

# Localization tasks
@task
def push(ctx):
    """Rebuild and push the source language to Transifex"""
    with ctx.cd(os.path.join(ROOT_PATH, 'readthedocs')):
        ctx.run('django-admin makemessages -l en')
        ctx.run('tx push -s')
        ctx.run('django-admin compilemessages -l en')


@task
def pull(ctx):
    """Pull the updated translations from Transifex"""
    with ctx.cd(os.path.join(ROOT_PATH, 'readthedocs')):
        ctx.run('tx pull -f ')
        ctx.run('django-admin makemessages --all')
        ctx.run('django-admin compilemessages')


@task
def docs(ctx, regenerate_config=False, push=False):
    """Pull and push translations to Transifex for our docs"""
    with ctx.cd(os.path.join(ROOT_PATH, 'docs')):
        # Update our tanslations
        ctx.run('tx pull -a')
        # Update resources
        if regenerate_config:
            os.remove(os.path.join(ROOT_PATH, 'docs', '.tx', 'config'))
            ctx.run('sphinx-intl create-txconfig')
        ctx.run('sphinx-intl update-txconfig-resources --transifex-project-name readthedocs-docs')
        # Rebuild
        ctx.run('sphinx-intl build')
        ctx.run('make gettext')
        # Push new ones
        if push:
            ctx.run('tx push -s')


namespace.add_collection(
    Collection(
        push,
        pull,
        docs,
    ),
    name='l10n',
)
