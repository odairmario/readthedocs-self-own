import mock
import pytest
from django_dynamic_fixture import get

from readthedocs.builds.constants import BRANCH, LATEST, TAG
from readthedocs.builds.models import (
    RegexAutomationRule,
    Version,
    VersionAutomationRule,
)
from readthedocs.projects.models import Project


@pytest.mark.django_db
class TestRegexAutomationRules:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.project = get(Project)

    @pytest.mark.parametrize(
        'version_name,regex,result',
        [
            # Matches all
            ('master', r'.*', True),
            ('latest', r'.*', True),

            # Contains match
            ('master', r'master', True),
            ('master-something', r'master', True),
            ('something-master', r'master', True),
            ('foo', r'master', False),

            # Starts with match
            ('master', r'^master', True),
            ('master-foo', r'^master', True),
            ('foo-master', r'^master', False),

            # Ends with match
            ('master', r'master$', True),
            ('foo-master', r'master$', True),
            ('master-foo', r'master$', False),

            # Exact match
            ('master', r'^master$', True),
            ('masterr', r'^master$', False),
            ('mmaster', r'^master$', False),

            # Match versions from 1.3.x series
            ('1.3.2', r'^1\.3\..*', True),
            ('1.3.3.5', r'^1\.3\..*', True),
            ('1.3.3-rc', r'^1\.3\..*', True),
            ('1.2.3', r'^1\.3\..*', False),

            # Some special regex scape characters
            ('12-a', r'^\d{2}-\D$', True),
            ('1-a', r'^\d{2}-\D$', False),

            # Groups
            ('1.3-rc', r'^(\d\.?)*-(\w*)$', True),

            # Bad regex
            ('master', r'*', False),
            ('master', r'?', False),
        ]
    )
    @pytest.mark.parametrize('version_type', [BRANCH, TAG])
    def test_match(
            self, version_name, regex, result, version_type):
        version = get(
            Version,
            verbose_name=version_name,
            project=self.project,
            active=False,
            type=version_type,
            built=False,
        )
        rule = get(
            RegexAutomationRule,
            project=self.project,
            priority=0,
            match_arg=regex,
            action=VersionAutomationRule.ACTIVATE_VERSION_ACTION,
            version_type=version_type,
        )
        assert rule.run(version) is result

    @mock.patch('readthedocs.builds.automation_actions.trigger_build')
    def test_action_activation(self, trigger_build):
        version = get(
            Version,
            verbose_name='v2',
            project=self.project,
            active=False,
            type=TAG,
        )
        rule = get(
            RegexAutomationRule,
            project=self.project,
            priority=0,
            match_arg='.*',
            action=VersionAutomationRule.ACTIVATE_VERSION_ACTION,
            version_type=TAG,
        )
        assert rule.run(version) is True
        assert version.active is True
        trigger_build.assert_called_once()

    def test_action_set_default_version(self):
        version = get(
            Version,
            verbose_name='v2',
            project=self.project,
            active=True,
            type=TAG,
        )
        rule = get(
            RegexAutomationRule,
            project=self.project,
            priority=0,
            match_arg='.*',
            action=VersionAutomationRule.SET_DEFAULT_VERSION_ACTION,
            version_type=TAG,
        )
        assert self.project.get_default_version() == LATEST
        assert rule.run(version) is True
        assert self.project.get_default_version() == version.slug


@pytest.mark.django_db
class TestAutomationRuleManager:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.project = get(Project)

    def test_append_rule_regex(self):
        assert not self.project.automation_rules.all()

        rule = RegexAutomationRule.objects.append_rule(
            project=self.project,
            description='First rule',
            match_arg='.*',
            version_type=TAG,
            action=VersionAutomationRule.ACTIVATE_VERSION_ACTION,
        )

        # First rule gets added with priority 0
        assert self.project.automation_rules.count() == 1
        assert rule.priority == 0

        # Adding a second rule
        rule = RegexAutomationRule.objects.append_rule(
            project=self.project,
            description='Second rule',
            match_arg='.*',
            version_type=BRANCH,
            action=VersionAutomationRule.ACTIVATE_VERSION_ACTION,
        )
        assert self.project.automation_rules.count() == 2
        assert rule.priority == 1

        # Adding a rule with a not secuencial priority
        rule = get(
            RegexAutomationRule,
            description='Third rule',
            project=self.project,
            priority=9,
            match_arg='.*',
            version_type=TAG,
            action=VersionAutomationRule.ACTIVATE_VERSION_ACTION,
        )
        assert self.project.automation_rules.count() == 3
        assert rule.priority == 9

        # Adding a new rule
        rule = RegexAutomationRule.objects.append_rule(
            project=self.project,
            description='Fourth rule',
            match_arg='.*',
            version_type=BRANCH,
            action=VersionAutomationRule.ACTIVATE_VERSION_ACTION,
        )
        assert self.project.automation_rules.count() == 4
        assert rule.priority == 10


@pytest.mark.django_db
class TestAutomationRuleMove:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.project = get(Project)
        self.rule_0 = self._append_rule('Zero')
        self.rule_1 = self._append_rule('One')
        self.rule_2 = self._append_rule('Two')
        self.rule_3 = self._append_rule('Three')
        self.rule_4 = self._append_rule('Four')
        self.rule_5 = self._append_rule('Five')
        assert self.project.automation_rules.count() == 6

    def _append_rule(self, description):
        rule = RegexAutomationRule.objects.append_rule(
            project=self.project,
            description=description,
            match_arg='.*',
            version_type=BRANCH,
            action=VersionAutomationRule.ACTIVATE_VERSION_ACTION,
        )
        return rule

    def test_move_rule_one_step(self):
        self.rule_0.move(1)
        new_order = [
            self.rule_1,
            self.rule_0,
            self.rule_2,
            self.rule_3,
            self.rule_4,
            self.rule_5,
        ]

        for priority, rule in enumerate(self.project.automation_rules.all()):
            assert rule == new_order[priority]
            assert rule.priority == priority

    def test_move_rule_positive_steps(self):
        self.rule_1.move(1)
        self.rule_1.move(2)

        new_order = [
            self.rule_0,
            self.rule_2,
            self.rule_3,
            self.rule_4,
            self.rule_1,
            self.rule_5,
        ]

        for priority, rule in enumerate(self.project.automation_rules.all()):
            assert rule == new_order[priority]
            assert rule.priority == priority

    def test_move_rule_positive_steps_overflow(self):
        self.rule_2.move(3)
        self.rule_2.move(2)

        new_order = [
            self.rule_0,
            self.rule_2,
            self.rule_1,
            self.rule_3,
            self.rule_4,
            self.rule_5,
        ]

        for priority, rule in enumerate(self.project.automation_rules.all()):
            assert rule == new_order[priority]
            assert rule.priority == priority

    def test_move_rules_positive_steps(self):
        self.rule_2.move(2)
        self.rule_0.refresh_from_db()
        self.rule_0.move(7)
        self.rule_4.refresh_from_db()
        self.rule_4.move(4)
        self.rule_1.refresh_from_db()
        self.rule_1.move(1)

        new_order = [
            self.rule_4,
            self.rule_1,
            self.rule_0,
            self.rule_3,
            self.rule_2,
            self.rule_5,
        ]

        for priority, rule in enumerate(self.project.automation_rules.all()):
            assert rule == new_order[priority]
            assert rule.priority == priority

    def test_move_rule_one_negative_step(self):
        self.rule_3.move(-1)
        new_order = [
            self.rule_0,
            self.rule_1,
            self.rule_3,
            self.rule_2,
            self.rule_4,
            self.rule_5,
        ]

        for priority, rule in enumerate(self.project.automation_rules.all()):
            assert rule == new_order[priority]
            assert rule.priority == priority

    def test_move_rule_negative_steps(self):
        self.rule_4.move(-1)
        self.rule_4.move(-2)

        new_order = [
            self.rule_0,
            self.rule_4,
            self.rule_1,
            self.rule_2,
            self.rule_3,
            self.rule_5,
        ]

        for priority, rule in enumerate(self.project.automation_rules.all()):
            assert rule == new_order[priority]
            assert rule.priority == priority

    def test_move_rule_negative_steps_overflow(self):
        self.rule_2.move(-3)
        self.rule_2.move(-2)

        new_order = [
            self.rule_0,
            self.rule_1,
            self.rule_3,
            self.rule_2,
            self.rule_4,
            self.rule_5,
        ]

        for priority, rule in enumerate(self.project.automation_rules.all()):
            assert rule == new_order[priority]
            assert rule.priority == priority

    def test_move_rules_negative_steps(self):
        self.rule_2.move(-2)
        self.rule_5.refresh_from_db()
        self.rule_5.move(-7)
        self.rule_3.refresh_from_db()
        self.rule_3.move(-2)
        self.rule_1.refresh_from_db()
        self.rule_1.move(-1)

        new_order = [
            self.rule_2,
            self.rule_3,
            self.rule_1,
            self.rule_0,
            self.rule_5,
            self.rule_4,
        ]

        for priority, rule in enumerate(self.project.automation_rules.all()):
            assert rule == new_order[priority]
            assert rule.priority == priority

    def test_move_rules_up_and_down(self):
        self.rule_2.move(2)
        self.rule_5.refresh_from_db()
        self.rule_5.move(-3)
        self.rule_3.refresh_from_db()
        self.rule_3.move(4)
        self.rule_1.refresh_from_db()
        self.rule_1.move(-1)

        new_order = [
            self.rule_0,
            self.rule_1,
            self.rule_3,
            self.rule_5,
            self.rule_4,
            self.rule_2,
        ]

        for priority, rule in enumerate(self.project.automation_rules.all()):
            assert rule == new_order[priority]
            assert rule.priority == priority
