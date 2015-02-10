#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Rasmus Sorensen, rasmusscholer@gmail.com <scholer.github.io>

##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License

# pylint: disable=C0301,R0913

"""

Module for communicating with Instapaper service.


Instapaper clients:
* github.com/rsgalloway/instapaper, (oauth2 + urllib)
* - pypi.python.org/pypi/instapaper/0.2 (uses urllib2 and oauth2, 2013, almost completely devoid of documentation and examples)
* github.com/mrtazz/InstapaperLibrary (only uses urllib and urllib2 - not sure how the hell this works, does not seem to perform any request signing.)
* - pypi.python.org/pypi/instapaperlib (from 2012, also uses urllib)
* github.com/jarodl/instayc, pypi.python.org/pypi/instayc  (uses instapaperlib)

Ruby:
* github.com/stve/instapaper (Ruby)
* github.com/mantas/instapaper-kindle (Ruby, linux command line, to get kindle mobi files)
* github.com/rtoohil/Reading-List-to-Instapaper
* github.com/stve/omniauth-instapaper

"""

from xauth_session import XAuthSession
import json


class InstapaperClient(object):
    """
    Object to interact with Instapaper server.
    Endpoints:
        /api/1.1/oauth/access_token
        /api/1.1/account/verify_credentials
        /api/1.1/bookmarks/add
        /api/1.1/folders/list
        /api/1.1/bookmarks/<bookmark-id>/highlight
    """
    def __init__(self, config, client_key, client_secret, username=None, password='', headers=None, apiurl=None):
        self.session = XAuthSession(client_key, client_secret)
        self.username = username # This might change. Should be a property that queries the header..
        if headers:
            self.session.headers.update(headers)
        if username:
            self.login(username, password)
        self.apiurl = apiurl or 'https://www.instapaper.com/api/1.1/'

    def get_resource(self, res):
        return urljoin(self.apiurl, resource)


    def login(self, username, password=''):
        url = self.get_resource('oauth/access_token')
        if not username:
            print("No username provided, will not attempt login..")
        r = self.session.request_access_tokens(url, username, password)
        r = self.post('account/verify_credentials')
        # r.json() has keys "user_id" and "username".
        self.username = r.json()["username"]


    def post(self, endpoint, data=None):
        """
        Instapaper specifies that parameters are never sent in the query string.
        """
        url = self.get_resource(endpoint)
        return self.session.post(url, data=data)

    def check_errors(self, response):
        pass

    def check_response(self, response, json=True):
        return response.json()


    ########################
    ##  Bookmark methods  ##
    ########################


    def list_bookmarks(self, limit=25, folder_id=None, have=None, highlights=None):
        """ List bookmarks.
        Input parameters:
            limit: Optional. A number between 1 and 500, default 25.
            folder_id: Optional. Possible values are unread (default), starred, archive, or a folder_id value from /api/1.1/folders/list.
            have: Optional. A concatenation of bookmark_id values that the client already has from the specified folder. See below.
            highlights: Optional. A '-' delimited list of highlight IDs that the client already has from the specified bookmarks.
        """
        have = ensure_string(have)
        highlights = ensure_string(highlights)
        data = {'limit': limit, 'folder_id': folder_id, 'have': have, 'highlights': highlights}
        data = {k: v for k, v in data if v is not None}
        r = self.post('bookmarks/list', data=data)
        return self.check_response(r)


    def add_bookmark(self, title=None, description=None, folder_id=None, resolve_final_url=1,
                     content=None, is_private_from_source=0):
        """
        Add a bookmark.
        Uh... If parameters are passed in the body as a urlencoded line.. How do I pass the content?
        - should the content be escaped in any way?
        """
        data = {'title': title, 'description': description, 'folder_id': folder_id, 'resolve_final_url': resolve_final_url, 'content': content, 'is_private_from_source': is_private_from_source}
        data = {k: v for k, v in data if v is not None}
        r = self.post('bookmarks/add', data=data)
        return self.check_response(r)

    def delete_bookmark(self, bookmark_id):
        r = self.post('bookmarks/delete', data={'bookmark_id': bookmark_id})
        return self.check_response(r)

    def star_bookmark(self, bookmark_id):
        r = self.post('bookmarks/star', data={'bookmark_id': bookmark_id})
        return self.check_response(r)

    def archive_bookmark(self, bookmark_id):
        r = self.post('bookmarks/archive', data={'bookmark_id': bookmark_id})
        return self.check_response(r)

    def unarchive_bookmark(self, bookmark_id):
        r = self.post('bookmarks/unarchive', data={'bookmark_id': bookmark_id})
        return self.check_response(r)

    def move_bookmark(self, bookmark_id, folder_id):
        r = self.post('bookmarks/move', data={'bookmark_id': bookmark_id, 'folder_id': folder_id})
        return self.check_response(r)

    def unarchive_bookmark(self, bookmark_id):
        r = self.post('bookmarks/get_text', data={'bookmark_id': bookmark_id})
        return self.check_errors(r)




    ######################
    ##  Folder methods  ##
    ######################

    def list_folders(self):
        r = self.post('folders/list')
        return self.check_response(r)

    def add_folder(self, title):
        r = self.post('folders/add', data={'title': title})
        return self.check_response(r)

    def delete_folders(self, folder_id):
        r = self.post('folders/delete', data={'folder_id': folder_id})
        return self.check_response(r)

    def delete_folders(self, order):
        r = self.post('folders/set_order', data={'order': order})
        return self.check_response(r)



    #########################
    ##  Highlight methods  ##
    #########################

    def bookmark_highlights(self, bookmark_id):
        r = self.post('bookmarks/%d/highlights' % bookmark_id)
        return self.check_response(r)

    def bookmark_highlight(self, bookmark_id, text, position):
        r = self.post('bookmarks/%d/highlight' % bookmark_id,
                      data={'text': text, 'position': position})
        return self.check_response(r)

    def delete_highlight(self, highlight_id):
        r = self.post('highlights/%d/delete' % highlight_id)
        return self.check_response(r)




def make_dict_def(kwst):
    """
    kwst in the style of:
        "limit=25, folder_id=None, have=None, highlights=None"
    Returns a string that defines a dict like:
        {'limit': limit, 'folder_id': folder_id, 'have': have, 'highlights': highlights}
    """
    keys = [elem.strip().split('=')[0] for elem in kwst.split(',')]
    s = "{%s}" % ", ".join("'{0}': {0}".format(k) for k in keys)
    return s


def ensure_string(value, delimiter=','):
    if value and isinstance(value, (list, set, tuple)):
        value = ",".join(value)
    return value
