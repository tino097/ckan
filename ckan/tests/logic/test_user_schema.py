# encoding: utf-8
"""Tests for the IUserForm hooks in the user schemas."""
from unittest import mock

import pytest

import ckan.plugins as p
import ckan.logic.schema as schema


class _AddField:
    def __init__(self, name):
        self.name = name

    def user_schema(self, user_schema):
        user_schema[self.name] = []
        user_schema[self.name + "_seen_previous"] = list(user_schema)
        return user_schema


@pytest.fixture
def user_form_plugins():
    implementations = []

    def _implementations(interface):
        if interface is p.IUserForm:
            return implementations
        return []

    with mock.patch.object(
        schema.plugins, "PluginImplementations", _implementations
    ):
        yield implementations


@pytest.mark.parametrize("schema_func", [
    schema.default_user_schema,
    schema.default_update_user_schema,
    schema.user_new_form_schema,
    schema.user_edit_form_schema,
    schema.create_user_for_user_invite_schema,
])
def test_plugin_field_is_in_every_user_schema(schema_func, user_form_plugins):
    user_form_plugins.append(_AddField("colour"))

    assert "colour" in schema_func()


def test_plugins_receive_the_schema_of_previous_plugins(user_form_plugins):
    user_form_plugins.extend([_AddField("first"), _AddField("second")])

    user_schema = schema.default_user_schema()

    assert "first" in user_schema["second_seen_previous"]
    assert "first" in user_schema and "second" in user_schema
