==========================================================
Adding custom fields to users using IUserForm
==========================================================

.. versionadded:: 2.13

The :py:class:`~ckan.plugins.interfaces.IUserForm` plugin interface lets an
extension add fields to the user API and to the registration and edit forms.
The values are stored in the ``plugin_extras`` column of the user. That column
is private: only a sysadmin can read or write it directly. A field becomes
visible to other users only when your plugin loads it into the result of
``user_show``.

The complete source of this example is in
https://github.com/ckan/ckan/tree/master/ckanext/example_iuserform


Storing a field
---------------

``user_schema`` receives the user schema and returns it. Every plugin that
implements the interface is called in turn, so several plugins can each add
their own fields. The schema is used by ``user_create``, ``user_update`` and
the user forms.

:py:func:`~ckan.logic.converters.store_plugin_extra` stores the value under the
name of your plugin, so it never mixes with the data of other plugins. Values
that are already stored are kept when a user is updated.

.. literalinclude:: ../../ckanext/example_iuserform/plugin.py
    :language: python
    :pyobject: _user_fields


Returning a field
-----------------

``show_user_schema`` starts as an empty schema. Add a field to it for every
value that ``user_show`` should return. The value is also returned by
``user_create`` and ``user_update``.
:py:func:`~ckan.logic.converters.load_plugin_extra` must be the first
validator of the field. Validators such as ``ignore_missing`` remove fields that
are not in the input, so a loader placed after them never runs.

.. literalinclude:: ../../ckanext/example_iuserform/plugin.py
    :language: python
    :pyobject: _show_fields

Values you do not add to this schema stay private.


Adding the field to the forms
-----------------------------

The registration and edit forms have an ``extra_fields`` block. Extend the form
templates and add your input to the block:

.. literalinclude:: ../../ckanext/example_iuserform/templates/user/edit_user_form.html
    :language: jinja

The same block exists in ``user/new_user_form.html``. To show the value on the
profile page, extend the ``user_about`` block of ``user/snippets/info.html``.
