from datetime import datetime

from django.contrib.auth.models import User
from django.core import management
from django.db.models import Sum

import tower
from nose.tools import eq_, ok_
from test_utils import TestCase

from badges.models import BadgeInstance, Category
from badges.tests import ModelsTestCase
from badges.tests.models import MultiTableParent, MultiTableChild


class ModelBaseTests(TestCase):
    def setUp(self):
        # Ensure xx locale is compiled
        management.call_command('compilemessages', locale='xx')

        tower.activate('xx')

    def tearDown(self):
        tower.deactivate_all()

    def localized_basic_test(self):
        # Category inherits from ModelBase
        c = Category.objects.create(name='TestString')

        eq_(c.localized('name'), 'TranslatedTestString')

    def localized_cache_test(self):
        c = Category.objects.create(name='TestString')
        ok_('name' not in c._localized_attrs)

        c.localized('name')
        ok_('name' in c._localized_attrs)


class MultiTableParentModelTests(ModelsTestCase):
    apps = ['badges.tests']

    def setUp(self):
        self.child = MultiTableChild.objects.create(some_value=10)

    def test_child(self):
        parent = MultiTableParent.objects.all()[0]
        eq_(parent.child_type, 'multitablechild')
        eq_(parent.child(), self.child)


class FakeDatetime(datetime):
    def __new__(cls, *args, **kwargs):
        return datetime.__new__(datetime, *args, **kwargs)


class BadgeInstanceTests(TestCase):
    fixtures = ['badge_instance']

    def setUp(self):
        self.badge_instance = BadgeInstance.objects.all()[0]

    def test_add_click(self):
        old_clicks = (self.badge_instance.clickstats_set
                      .aggregate(Sum('clicks'))['clicks__sum'])

        self.badge_instance.add_click()

        new_clicks = (self.badge_instance.clickstats_set
                      .aggregate(Sum('clicks'))['clicks__sum'])
        eq_(old_clicks + 1, new_clicks)

    def test_for_user_by_category(self):
        user = User.objects.get(pk=5)
        categories = BadgeInstance.objects.for_user_by_category(user)
        expect = {'Firefox': [self.badge_instance]}
        eq_(categories, expect)