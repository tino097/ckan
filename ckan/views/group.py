# encoding: utf-8

import logging
import datetime
from urllib import urlencode

from pylons.i18n import get_lang

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic
import ckan.lib.search as search
import ckan.model as model
import ckan.authz as authz
import ckan.lib.plugins
import ckan.plugins as plugins
from ckan.common import OrderedDict, c, config, request, _
from flask import Blueprint
import ckan.lib.plugins as lib_plugins

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params


log = logging.getLogger(__name__)

group = Blueprint('group_org', __name__, url_prefix=u'/<group_type>')
# organization = Blueprint('organization', __name__, url_prefix=u'/organization')
group_type = None

lookup_group_plugin = ckan.lib.plugins.lookup_group_plugin
lookup_group_controller = ckan.lib.plugins.lookup_group_controller


def _index_template(group_type):
    return lookup_group_plugin(group_type).index_template()


def _group_form(group_type=None):
    return lookup_group_plugin(group_type).group_form()


def _form_to_db_schema(group_type=None):
    return lookup_group_plugin(group_type).form_to_db_schema()


def _db_to_form_schema(group_type=None):
    '''This is an interface to manipulate data from the database
    into a format suitable for the form (optional)'''
    return lookup_group_plugin(group_type).db_to_form_schema()


def _setup_template_variables(context, data_dict, group_type=None):
    return lookup_group_plugin(group_type).\
        setup_template_variables(context, data_dict)


def _new_template(group_type):
    return lookup_group_plugin(group_type).new_template()


def _about_template(group_type):
    return lookup_group_plugin(group_type).about_template()


def _read_template(group_type):
    return lookup_group_plugin(group_type).read_template()


def _history_template(group_type):
    return lookup_group_plugin(group_type).history_template()


def _edit_template(group_type):
    return lookup_group_plugin(group_type).edit_template()


def _activity_template(group_type):
    return lookup_group_plugin(group_type).activity_template()


def _admins_template(group_type):
    return lookup_group_plugin(group_type).admins_template()


def _bulk_process_template(group_type):
    return lookup_group_plugin(group_type).bulk_process_template()


# end hooks
def _replace_group_org(string):
    ''' substitute organization for group if this is an org'''
    return string


def _action(action_name):
    ''' select the correct group/org action '''
    return get_action(_replace_group_org(action_name))


def _check_access(action_name, *args, **kw):
    ''' select the correct group/org check_access '''
    return check_access(_replace_group_org(action_name), *args, **kw)


def _render_template(template_name, group_type):
    ''' render the correct group/org template '''
    return base.render(
        _replace_group_org(template_name),
        extra_vars={'group_type': group_type})


def _redirect_to_this_controller(*args, **kw):
    ''' wrapper around redirect_to but it adds in this request's controller
    (so that it works for Organization or other derived controllers)'''
    kw['controller'] = request.environ['pylons.routes_dict']['controller']
    return h.redirect_to(*args, **kw)


def _url_for_this_controller(  *args, **kw):
    ''' wrapper around url_for but it adds in this request's controller
    (so that it works for Organization or other derived controllers)'''
    kw['controller'] = request.environ['pylons.routes_dict']['controller']
    return h.url_for(*args, **kw)


def _guess_group_type(expecting_name=False):
    """
    Guess the type of group from the URL.
    * The default url '/group/xyz' returns None
    * group_type is unicode
    * this handles the case where there is a prefix on the URL
    (such as /data/organization)
    """
    parts = [x for x in request.path.split('/') if x]

    idx = -1
    if expecting_name:
        idx = -2

    gt = parts[idx]
    return gt


@group.url_value_preprocessor
def guess_group_type(endpoint, values):
    print endpoint
    print values


def index(group_type='group'):
    group_type = _guess_group_type() or 'group'
    page = h.get_page_number(request.params) or 1
    items_per_page = 21

    context = {'model': model, 'session': model.Session,
               'user': c.user, 'for_view': True,
               'with_private': False}

    q = c.q = request.params.get('q', '')
    sort_by = c.sort_by_selected = request.params.get('sort')
    try:
        _check_access('site_read', context)
        _check_access('group_list', context)
    except NotAuthorized:
        base.abort(403, _(u'Not authorized to see this page'))

    # pass user info to context as needed to view private datasets of
    # orgs correctly
    if c.userobj:
        context['user_id'] = c.userobj.id
        context['user_is_admin'] = c.userobj.sysadmin

    try:
        data_dict_global_results = {
                'all_fields': False,
                'q': q,
                'sort': sort_by,
                'type': group_type or 'group',
            }
        global_results =  _action('group_list')(
                context, data_dict_global_results)
    except ValidationError as e:
        if e.error_dict and e.error_dict.get('message'):
            msg = e.error_dict['message']
        else:
            msg = str(e)
        h.flash_error(msg)
        c.page = h.Page([], 0)
        return base.render(_index_template(group_type),
                           extra_vars={'group_type': group_type})

    data_dict_page_results = {
            'all_fields': True,
            'q': q,
            'sort': sort_by,
            'type': group_type or 'group',
            'limit': items_per_page,
            'offset': items_per_page * (page - 1),
            'include_extras': True
        }
    page_results = _action('group_list')(context, data_dict_page_results)

    c.page = h.Page(
            collection=global_results,
            page=page,
            url=h.pager_url,
            items_per_page=items_per_page,
        )

    c.page.items = page_results
    base.render(_index_template(group_type),
                extra_vars={'group_type': group_type})


def read(id):
    print id


def new():
    print 'hi'


# Routing
group.add_url_rule(u'/', methods=[u'GET'], view_func=index)
# group.add_url_rule(u'/<group-type>', methods=[u'GET'], view_func=index)
# group.add_url_rule(u'/organization/read', methods=[u'GET'], view_func=read)

# organization.add_url_rule(u'/', methods=[u'GET'], view_func=index)
