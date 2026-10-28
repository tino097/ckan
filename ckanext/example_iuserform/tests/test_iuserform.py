# encoding: utf-8
import pytest
import sqlalchemy as sa

import ckan.model as model
import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
from ckan.lib.helpers import url_for


def _stored_extras(user):
    model.Session.expire_all()
    return model.User.get(user["id"]).plugin_extras


@pytest.mark.ckan_config("ckan.plugins", "example_iuserform")
@pytest.mark.usefixtures("non_clean_db", "with_plugins")
class TestExampleIUserFormApi(object):
    def test_value_is_stored_in_private_plugin_extras(self):
        user = factories.User(favourite_colour="green")

        assert _stored_extras(user) == {
            "example_iuserform": {"favourite_colour": "green"}}

    def test_value_is_returned_by_user_show_to_anonymous(self):
        user = factories.User(favourite_colour="green")

        shown = helpers.call_action(
            "user_show", context={"user": "", "ignore_auth": False},
            id=user["id"])

        assert shown["favourite_colour"] == "green"
        assert "plugin_extras" not in shown

    def test_update_keeps_data_of_other_plugins(self):
        user = factories.User(plugin_extras={"other": {"key": "kept"}})

        updated = helpers.call_action(
            "user_update", id=user["id"], email=user["email"],
            favourite_colour="red")

        assert updated["favourite_colour"] == "red"
        assert _stored_extras(user) == {
            "other": {"key": "kept"},
            "example_iuserform": {"favourite_colour": "red"},
        }

    def test_update_without_value_keeps_stored_value(self):
        user = factories.User(favourite_colour="green")

        helpers.call_action(
            "user_update", id=user["id"], email=user["email"],
            fullname="New Name")

        assert _stored_extras(user) == {
            "example_iuserform": {"favourite_colour": "green"}}

    def test_regular_user_cannot_write_plugin_extras_directly(self):
        user = factories.User()
        context = {"user": user["name"], "ignore_auth": False}

        helpers.call_action(
            "user_update", context=context, id=user["id"],
            email=user["email"], favourite_colour="red",
            plugin_extras={"evil": {"x": 1}})

        assert _stored_extras(user) == {
            "example_iuserform": {"favourite_colour": "red"}}

    def test_value_is_in_database_column(self):
        user = factories.User(favourite_colour="green")

        stored = model.Session.execute(
            sa.text('SELECT plugin_extras FROM "user" WHERE id=:id'),
            {"id": user["id"]},
        ).first()[0]

        assert stored["example_iuserform"]["favourite_colour"] == "green"


@pytest.mark.ckan_config("ckan.plugins", "example_iuserform")
@pytest.mark.ckan_config("ckan.auth.create_user_via_web", True)
@pytest.mark.usefixtures("non_clean_db", "with_plugins")
class TestExampleIUserFormWeb(object):
    def test_register_form_has_the_field(self, app):
        response = app.get(url_for("user.register"))

        assert 'name="favourite_colour"' in response

    def test_register_stores_the_value(self, app):
        stub = factories.User.stub()

        app.post(
            url_for("user.register"),
            data={
                "save": "",
                "name": stub.name,
                "email": stub.email,
                "password1": "TestPassword1",
                "password2": "TestPassword1",
                "favourite_colour": "purple",
            },
        )

        shown = helpers.call_action("user_show", id=stub.name)
        assert shown["favourite_colour"] == "purple"

    def test_edit_form_is_prefilled_and_saves(self, app):
        user = factories.UserWithToken(favourite_colour="green")
        headers = {"Authorization": user["token"]}
        url = url_for("user.edit", id=user["name"])

        response = app.get(url, headers=headers)
        assert 'value="green"' in response

        app.post(
            url,
            headers=headers,
            data={
                "save": "",
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "favourite_colour": "orange",
            },
        )

        assert helpers.call_action(
            "user_show", id=user["id"])["favourite_colour"] == "orange"

    def test_profile_page_shows_the_value(self, app):
        user = factories.User(favourite_colour="green")

        response = app.get(url_for("user.read", id=user["name"]))

        assert "green" in response
