# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.autoform import directives
from plone.supermodel import model

from dexterity.localrolesfield.field import LocalRolesField

from collective.task import _


class ICollectiveTaskLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ITaskContent(model.Schema):
    """ Interface for task content type """

    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True
    )

    parents_assigned_groups = LocalRolesField(
        title=_(u"Parents assigned groups"),
        required=False,
        value_type=schema.Choice(vocabulary=u'collective.task.AssignedGroups')
    )
    #directives.mode(parents_assigned_groups='hidden')

    parents_enquirers = LocalRolesField(
        title=_(u"Parents enquirers"),
        required=False,
        value_type=schema.Choice(vocabulary=u'collective.task.Enquirer')
    )
    #directives.mode(parents_enquirers='hidden')


class ITaskMethods(Interface):

    def get_highest_task_parent(task=False):
        """
            Get the object containing the highest ITask object
            or the highest ITask object if task is True
        """


class ITaskContentMethods(Interface):
    """ Adapter description """
