# -*- coding: utf-8 -*-

"""Integration utility functions."""

from __future__ import division, print_function, unicode_literals

import os
import six


def normalize_request_payload(request):
    """
    Normalize the request body, hopefully to JSON.

    This will attempt to return a JSON body, backing down to a string body next.

    :param request: HTTP request object
    :type request: django.http.HttpRequest
    :returns: The request body as a string
    :rtype: str
    """
    request_payload = getattr(request, 'data', {})
    if request.content_type != 'application/json':
        # Here, request_body can be a dict or a MergeDict. Probably best to
        # normalize everything first
        try:
            request_payload = dict(list(request_payload.items()))
        except AttributeError:
            pass
    return request_payload


def get_secret(size=64):
    """
    Get a random string of `size` bytes.

    :param size: Number of bytes
    """
    secret = os.urandom(size)
    if six.PY2:
        # On python two os.urandom returns str instead of bytes
        return secret.encode('hex')
    return secret.hex()
