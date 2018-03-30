#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `django-multiinfo` package."""

from click.testing import CliRunner

import django_multiinfo
from django_multiinfo import cli

django_multiinfo.__version__


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'django_multiinfo.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
