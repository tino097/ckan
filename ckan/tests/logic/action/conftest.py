# encoding: utf-8
from unittest import mock

import pytest

import ckan.logic.converters as converters
import ckan.plugins as p


class _ShowFields:
    def __init__(self, fields, validators=()):
        self.fields = fields
        self.validators = list(validators)

    def user_schema(self, user_schema):
        return user_schema

    def show_user_schema(self, user_schema):
        for field, plugin in self.fields.items():
            user_schema[field] = [
                converters.load_plugin_extra(plugin), *self.validators]
        return user_schema


@pytest.fixture
def show_user_fields():
    """Return a function that makes a fake IUserForm plugin expose
    ``plugin_extras`` values: ``add({"field": "plugin_name"}, validators)``.
    """
    implementations = []
    real = p.PluginImplementations

    def _implementations(interface):
        if interface is p.IUserForm:
            return implementations
        return real(interface)

    def add(fields, validators=()):
        implementations.append(_ShowFields(fields, validators))

    with mock.patch.object(p, "PluginImplementations", _implementations):
        yield add
