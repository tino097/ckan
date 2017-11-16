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

log = logging.getLogger(__name__)

group = Blueprint('group', __name__, url_prefix=None)
group_type = None


@group.before_request
def before_request():
    import pdb
    pdb.set_trace()
    group_type = _guess_group_type() or 'group'
    print group_type


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
    print gt
    return gt


def index():
    print 'hi'


# Routing
group.add_url_rule(u'/group', methods=[u'GET'], view_func=index)
