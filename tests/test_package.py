#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `django-multiinfo` package."""

import pytest
from django.contrib import admin
from django.test import TestCase
from django_powerbank.testing.base import MigrationsCheckMx

import django_multiinfo


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/wooyek/cookiecutter-pylib')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_version_exists():
    """This is a stupid test dummy validating import of django_multiinfo"""
    assert django_multiinfo.__version__


class TestAdmin(TestCase):
    def test_admin(self):
        admin.autodiscover()


class TestCommangs(TestCase):
    def test_checks(self):
        from django.core.management import BaseCommand
        BaseCommand().check(display_num_errors=True)


class MigrationsCheckTests(MigrationsCheckMx, TestCase):
    pass
