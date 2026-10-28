# encoding: utf-8
from __future__ import annotations

from ckan.common import CKANConfig
from ckan.types import Schema, Validator, ValidatorFactory
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

PLUGIN_NAME = "example_iuserform"


@tk.validator_args
def _user_fields(
        ignore_missing: Validator, unicode_safe: Validator,
        store_plugin_extra: ValidatorFactory) -> Schema:
    return {
        "favourite_colour": [
            ignore_missing, unicode_safe, store_plugin_extra(PLUGIN_NAME)],
    }


@tk.validator_args
def _show_fields(load_plugin_extra: ValidatorFactory) -> Schema:
    return {"favourite_colour": [load_plugin_extra(PLUGIN_NAME)]}


class ExampleIUserFormPlugin(plugins.SingletonPlugin):
    """Add a favourite colour to the user forms and the user API."""
    plugins.implements(plugins.IUserForm, inherit=True)
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_: CKANConfig):
        tk.add_template_directory(config_, "templates")

    # IUserForm

    def user_schema(self, schema: Schema) -> Schema:
        schema.update(_user_fields())
        return schema

    def show_user_schema(self, schema: Schema) -> Schema:
        schema.update(_show_fields())
        return schema
