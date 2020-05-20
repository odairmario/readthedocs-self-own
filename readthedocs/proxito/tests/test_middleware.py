# Copied from test_middleware.py

import sys

import pytest
from django.test import TestCase
from django.test.utils import override_settings
from django_dynamic_fixture import get

from readthedocs.projects.models import Domain, Project
from readthedocs.proxito.middleware import ProxitoMiddleware
from readthedocs.rtd_tests.base import RequestFactoryTestMixin
from readthedocs.rtd_tests.utils import create_user


@override_settings(PUBLIC_DOMAIN='dev.readthedocs.io')
@pytest.mark.proxito
class MiddlewareTests(RequestFactoryTestMixin, TestCase):

    def setUp(self):
        self.middleware = ProxitoMiddleware()
        self.url = '/'
        self.owner = create_user(username='owner', password='test')
        self.pip = get(
            Project,
            slug='pip',
            users=[self.owner],
            privacy_level='public'
        )

    def run_middleware(self, request):
        return self.middleware.process_request(request)

    def test_proper_cname(self):
        domain = 'docs.random.com'
        get(Domain, project=self.pip, domain=domain)
        request = self.request(self.url, HTTP_HOST=domain)
        res = self.run_middleware(request)
        self.assertIsNone(res)
        self.assertEqual(request.cname, True)
        self.assertEqual(request.host_project_slug, 'pip')

    def test_proper_cname_https_upgrade(self):
        cname = 'docs.random.com'
        get(Domain, project=self.pip, domain=cname, canonical=True, https=True)

        for url in (self.url, '/subdir/'):
            request = self.request(url, HTTP_HOST=cname)
            res = self.run_middleware(request)
            self.assertIsNone(res)
            self.assertTrue(hasattr(request, 'canonicalize'))
            self.assertEqual(request.canonicalize, 'https')

    def test_canonical_cname_redirect(self):
        """Requests to the public domain URL should redirect to the custom domain if the domain is canonical/https."""
        cname = 'docs.random.com'
        domain = get(Domain, project=self.pip, domain=cname, canonical=False, https=False)

        request = self.request(self.url, HTTP_HOST='pip.dev.readthedocs.io')
        res = self.run_middleware(request)
        self.assertIsNone(res)
        self.assertFalse(hasattr(request, 'canonicalize'))

        # Make the domain canonical/https and make sure we redirect
        domain.canonical = True
        domain.https = True
        domain.save()
        for url in (self.url, '/subdir/'):
            request = self.request(url, HTTP_HOST='pip.dev.readthedocs.io')
            res = self.run_middleware(request)
            self.assertIsNone(res)
            self.assertTrue(hasattr(request, 'canonicalize'))
            self.assertEqual(request.canonicalize, 'canonical-cname')

    # We are not canonicalizing custom domains -> public domain for now
    @pytest.mark.xfail(strict=True)
    def test_canonical_cname_redirect_public_domain(self):
        """Requests to a custom domain should redirect to the public domain or canonical domain if not canonical."""
        cname = 'docs.random.com'
        domain = get(Domain, project=self.pip, domain=cname, canonical=False, https=False)

        request = self.request(self.url, HTTP_HOST=cname)
        res = self.run_middleware(request)
        self.assertIsNone(res)
        self.assertTrue(hasattr(request, 'canonicalize'))
        self.assertEqual(request.canonicalize, 'noncanonical-cname')

        # Make the domain canonical and make sure we don't redirect
        domain.canonical = True
        domain.save()
        for url in (self.url, '/subdir/'):
            request = self.request(url, HTTP_HOST=cname)
            res = self.run_middleware(request)
            self.assertIsNone(res)
            self.assertFalse(hasattr(request, 'canonicalize'))

    def test_proper_cname_uppercase(self):
        get(Domain, project=self.pip, domain='docs.random.com')
        request = self.request(self.url, HTTP_HOST='docs.RANDOM.COM')
        self.run_middleware(request)
        self.assertEqual(request.cname, True)
        self.assertEqual(request.host_project_slug, 'pip')

    def test_invalid_cname(self):
        self.assertFalse(Domain.objects.filter(domain='my.host.com').exists())
        request = self.request(self.url, HTTP_HOST='my.host.com')
        r = self.run_middleware(request)
        # We show the 404 error page
        self.assertContains(r, 'my.host.com', status_code=404)

    def test_proper_subdomain(self):
        request = self.request(self.url, HTTP_HOST='pip.dev.readthedocs.io')
        self.run_middleware(request)
        self.assertEqual(request.subdomain, True)
        self.assertEqual(request.host_project_slug, 'pip')

    @override_settings(PUBLIC_DOMAIN='foo.bar.readthedocs.io')
    def test_subdomain_different_length(self):
        request = self.request(
            self.url, HTTP_HOST='pip.foo.bar.readthedocs.io'
        )
        self.run_middleware(request)
        self.assertEqual(request.subdomain, True)
        self.assertEqual(request.host_project_slug, 'pip')

    def test_request_header(self):
        request = self.request(
            self.url, HTTP_HOST='some.random.com', HTTP_X_RTD_SLUG='pip'
        )
        self.run_middleware(request)
        self.assertEqual(request.rtdheader, True)
        self.assertEqual(request.host_project_slug, 'pip')

    def test_request_header_uppercase(self):
        request = self.request(
            self.url, HTTP_HOST='some.random.com', HTTP_X_RTD_SLUG='PIP'
        )
        self.run_middleware(request)

        self.assertEqual(request.rtdheader, True)
        self.assertEqual(request.host_project_slug, 'pip')

    def test_long_bad_subdomain(self):
        domain = 'www.pip.dev.readthedocs.io'
        request = self.request(self.url, HTTP_HOST=domain)
        res = self.run_middleware(request)
        self.assertEqual(res.status_code, 400)


@override_settings(PUBLIC_DOMAIN='dev.readthedocs.io', ROOT_URLCONF='fake')
@pytest.mark.proxito
class MiddlewareURLConfTests(RequestFactoryTestMixin, TestCase):

    def setUp(self):
        self.owner = create_user(username='owner', password='test')
        self.domain = 'pip.dev.readthedocs.io'
        self.pip = get(
            Project,
            slug='pip',
            users=[self.owner],
            privacy_level='public',
            urlconf='subpath/to/$version/$language/$filename'  # Flipped
        )
        sys.modules['fake'] = self.pip.url_class

    def test_middleware_urlconf(self):
        resp = self.client.get('/subpath/to/testing/en/foodex.html', HTTP_HOST=self.domain)
        print(resp.resolver_match)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp['X-Accel-Redirect'],
            '/proxito/media/html/pip/testing/foodex.html',
        )

    def test_middleware_urlconf_invalid(self):
        resp = self.client.get('/subpath/to/latest/index.html', HTTP_HOST=self.domain)
        self.assertEqual(resp.status_code, 404)

    def test_middleware_urlconf_subpath_downloads(self):
        # These aren't configurable yet
        resp = self.client.get('/subpath/to/_/downloads/en/latest/pdf/', HTTP_HOST=self.domain)
        print(resp.resolver_match)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp['X-Accel-Redirect'],
            '/proxito/media/pdf/pip/latest/pip.pdf',
        )

    def test_middleware_urlconf_subpath_api(self):
        # These aren't configurable yet
        resp = self.client.get('/subpath/to/_/api/v2/footer_html/?project=pip&version=latest&language=en&page=index', HTTP_HOST=self.domain)
        print(resp.resolver_match)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(
            resp,
            'Inserted RTD Footer',
        )
