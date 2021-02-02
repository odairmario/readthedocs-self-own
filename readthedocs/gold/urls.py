# -*- coding: utf-8 -*-

"""Gold subscription URLs."""

from django.conf.urls import url
from django.views.generic.base import TemplateView

from readthedocs.gold import views
from readthedocs.projects.constants import PROJECT_SLUG_REGEX


urlpatterns = [
    url(r'^$', views.DetailGoldSubscription.as_view(), name='gold_detail'),
    url(
        r'^subscription/$',
        views.UpdateGoldSubscription.as_view(),
        name='gold_subscription',
    ),
    url(
        r'^subscription/checkout/create/$',
        views.GoldCreateCheckoutSession.as_view(),
        name='gold_checkout_create',
    ),
    url(
        r'^subscription/checkout/sucess/$',
        TemplateView.as_view(template_name=''),
        name='gold_checkout_success',
    ),
    url(
        r'^subscription/checkout/cancel/$',
        TemplateView.as_view(template_name=''),
        name='gold_checkout_cancel',
    ),
    url(
        r'^subscription/portal/$',
        views.GoldSubscriptionPortal.as_view(),
        name='gold_subscription_portal',
    ),
    url(r'^projects/$', views.GoldProjectsListCreate.as_view(), name='gold_projects'),
    url(
        (
            r'^projects/remove/(?P<project_slug>{project_slug})/$'.format(
                project_slug=PROJECT_SLUG_REGEX,
            )
        ),
        views.GoldProjectRemove.as_view(),
        name='gold_projects_remove',
    ),
]
