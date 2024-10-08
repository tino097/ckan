# encoding: utf-8

from ckan.types import Schema
import ckan.plugins as p
import ckan.plugins.toolkit as tk


class ExampleIDatasetFormPlugin(tk.DefaultDatasetForm, p.SingletonPlugin):
    p.implements(p.IDatasetForm)

    def create_package_schema(self) -> Schema:
        # let's grab the default schema in our plugin
        schema: Schema = super(
            ExampleIDatasetFormPlugin, self).create_package_schema()
        # our custom field
        schema.update({
            u'custom_text': [tk.get_validator(u'ignore_missing'),
                             tk.get_converter(u'convert_to_extras')]
        })
        schema.update({
            u'custom_number': [tk.get_validator(u'ignore_missing'),
                               tk.get_converter(u'convert_to_extras'),
                               tk.get_validator('int_validator')]
        })

        return schema

    def update_package_schema(self) -> Schema:
        schema: Schema = super(
            ExampleIDatasetFormPlugin, self).update_package_schema()
        # our custom field
        schema.update({
            u'custom_text': [tk.get_validator(u'ignore_missing'),
                             tk.get_converter(u'convert_to_extras')]
        })
        schema.update({
            u'custom_number': [tk.get_validator(u'ignore_missing'),
                               tk.get_converter(u'convert_to_extras')]
        })

        return schema

    def show_package_schema(self) -> Schema:
        schema: Schema = super(
            ExampleIDatasetFormPlugin, self).show_package_schema()
        schema.update({
            u'custom_text': [tk.get_converter(u'convert_from_extras'),
                             tk.get_validator(u'ignore_missing')],
            u'custom_text_2': [tk.get_converter(u'convert_from_extras'),
                               tk.get_validator(u'ignore_missing')],
            u'custom_number': [tk.get_converter(u'convert_from_extras'),
                               tk.get_validator(u'ignore_missing'),
                               tk.get_validator('int_validator')],

        })
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return [u'fancy_type']
