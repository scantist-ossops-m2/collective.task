# -*- coding: utf-8 -*-
import unittest2 as unittest
from zope.interface import Interface
from zope.lifecycleevent import modified, Attributes
from plone import api
from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID

from Products.CMFPlone.utils import base_hasattr
from ..testing import COLLECTIVE_TASK_FUNCTIONAL_TESTING


class TestSubscribers(unittest.TestCase):

    layer = COLLECTIVE_TASK_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestSubscribers, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.folder = api.content.create(container=self.portal, type='Folder', id='folder', title='Folder')
        self.task1 = api.content.create(container=self.portal, type='task', id='task1', title='Task1',
                                        assigned_group='Site Administrators')
        self.task2 = api.content.create(container=self.folder, type='task', id='task2', title='Task2',
                                        assigned_group='Administrators')
        self.task3 = api.content.create(container=self.task2, type='task', id='task3', title='Task3',
                                        assigned_group='Reviewers')
        self.task4 = api.content.create(container=self.task3, type='task', id='task4', title='Task4',
                                        assigned_group='')

    def test_afterTransitionITaskSubscriber(self):
        # assigned_user is None
        self.assertEqual(self.task1.assigned_user, None)
        api.content.transition(obj=self.task1, transition='do_to_assign')
        self.assertTrue(base_hasattr(self.task1, 'auto_to_do_flag'))
        self.assertFalse(self.task1.auto_to_do_flag)
        self.assertEqual(api.content.get_state(obj=self.task1), 'to_assign')
        api.content.transition(obj=self.task1, transition='back_in_created')
        # assigned_user is set
        self.task1.assigned_user = TEST_USER_ID
        api.content.transition(obj=self.task1, transition='do_to_assign')
        self.assertTrue(self.task1.auto_to_do_flag)
        self.assertEqual(api.content.get_state(obj=self.task1), 'to_do')
        # back in to assign
        api.content.transition(obj=self.task1, transition='back_in_to_assign')
        self.assertFalse(self.task1.auto_to_do_flag)
        self.assertEqual(api.content.get_state(obj=self.task1), 'to_assign')

    def test_taskContent_created(self):
        # check creation
        self.assertEqual(self.task1.parents_assigned_groups, None)
        self.assertEqual(self.task2.parents_assigned_groups, None)
        self.assertEqual(self.task3.parents_assigned_groups, ['Administrators'])
        self.assertListEqual(self.task4.parents_assigned_groups, ['Administrators', 'Reviewers'])
        # check copy
        api.content.copy(source=self.task2, target=self.task1)
        self.assertEqual(self.task1.parents_assigned_groups, None)
        self.assertEqual(self.task1['task2'].parents_assigned_groups, ['Site Administrators'])
        self.assertListEqual(self.task1['task2']['task3'].parents_assigned_groups,
                             ['Site Administrators', 'Administrators'])
        self.assertListEqual(self.task1['task2']['task3']['task4'].parents_assigned_groups,
                             ['Site Administrators', 'Administrators', 'Reviewers'])
        # check move
        api.content.delete(obj=self.task1['task2'])
        self.assertEqual(self.task1.objectIds(), [])
        api.content.move(source=self.task2, target=self.task1)
        self.assertEqual(self.task1.parents_assigned_groups, None)
        self.assertEqual(self.task2.parents_assigned_groups, ['Site Administrators'])
        self.assertListEqual(self.task3.parents_assigned_groups, ['Site Administrators', 'Administrators'])
        self.assertListEqual(self.task4.parents_assigned_groups,
                             ['Site Administrators', 'Administrators', 'Reviewers'])

    def test_taskContent_modified(self):
        # initial state
        self.assertEqual(self.task1.parents_assigned_groups, None)
        self.assertEqual(self.task2.parents_assigned_groups, None)
        self.assertEqual(self.task3.parents_assigned_groups, ['Administrators'])
        self.assertListEqual(self.task4.parents_assigned_groups, ['Administrators', 'Reviewers'])
        self.task2.assigned_group = 'Site Administrators'
        modified(self.task2, Attributes(Interface, "ITask.assigned_group"))
        self.assertEqual(self.task2.parents_assigned_groups, None)
        self.assertEqual(self.task3.parents_assigned_groups, ['Site Administrators'])
        self.assertListEqual(self.task4.parents_assigned_groups, ['Site Administrators', 'Reviewers'])
