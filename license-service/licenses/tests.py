"""
Licenses Tests
"""

from django.test import TestCase


def test_dummy(client):
    result = 1 + 1
    assert result == 2
