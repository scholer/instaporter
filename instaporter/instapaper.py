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

# pylint: disable=C0103,C0301,R0902,R0904,R0913

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

import os
from urllib.parse import urljoin#, urlsplit
#import json
import pickle
#from six import string_types
import logging
logger = logging.getLogger(__name__)


from .xauth_session import XAuthSession
from .utils import credentials_prompt, load_config, save_config#, load_consumer_keys


__version__ = 0.1



def is_error(response):
    """
    Check response for errors.
    Returns False if response is OK.
    If response has HTTP status code larger than or equal to 300,
    the HTTP status code is returned.
    If the response is an Instapaper API error, the
    API error's error_code is returned.
    If the data cannot be parsed as json, return 1.
    If the data does not have a type, return 2.
    Note that the data could be an empty list;
    that it not interpreted as an error.
    """
    if response.status_code >= 300:
        return response.status
    try:
        data = response.json()
    except ValueError:
        return 1
    if len(data) == 0:
        print("Empty response (but that's not neccesarily an error, could be empty list):", response)
        return 0
    try:
        if data[0]["type"] == "error":
            return data[0]["error_code"]
        else:
            return False
    except KeyError:
        print("What the fuck, response has no type?! --", data)
        return 2



def save_cookies(fd, cookiejar):
    """ Save cookiejar to file. """
    pickle.dump(cookiejar, fd)

def load_cookies(fd):
    """ Load cookies from file. """
    return pickle.load(fd)





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

    pass_prompt = credentials_prompt

    def __init__(self, config=None, client_key=None, client_secret=None,
                 username=None, password='', headers=None, config_filepath=None):
        """
        filename or filepath?
         -- filepath is the better choice, because filename is sometimes
            interpreted as basename (myfile.txt) and sometimes the full
            (absolute or relative) path, /path/to/myfile.txt or ../to/myfile.txt
        """
        # Check whether config is a string (filepath) or dict:
        self.config = config or {}
        self.config_filepath = config_filepath
        if self.config_filepath:
            self.load_config()
        # Note: The username might change over time. Could be a property that queries the latest request header.
        self._username = username
        self._password = password
        self.status = False
        self.apiurl = config.get('apiurl') or 'https://www.instapaper.com/api/1.1/'
        # Create xauth session:
        self.session = XAuthSession(client_key, client_secret)
        # Update headers:
        if self.config.get('headers'):
            self.headers.update(self.config['headers'])
        if headers:
            self.headers.update(headers)
        if "User-Agent" not in self.headers:
            self.headers["User-Agent"] = "Instaporter-InstaClient/%s github.com/scholer/Instaporter - rasmusscholer@gmail.com" % __version__
        if self.cookies_filepath:
            self.load_cookies()
        # Update access_tokens:
        if 'access_tokens' in config:
            self.update_access_tokens(config['access_tokens'])
            userinfo = self.verify_credentials()
            logger.info("xAuth using existing access_tokens returned: %s", userinfo)
            if userinfo:
                logger.info("-- existing tokens seem OK, will not attempt to obtain new..")
                return
        # Continue with login, unless disabled:
        if config.get('instapaper_login_prompt', True) and (not username or not password):
            username, password = credentials_prompt(self.username)
        if username and password is not False:
            self.status = bool(self.login(username, password))

    @property
    def username(self):
        """ Username property. Returns self._username if set, otherwise config['username']. """
        return self._username or self.config.get('instapaper_username')
    @username.setter
    def username(self, value):
        """ Set username.
        If self._password has previously been set (e.g. on instantiation),
        self._username is set. Else if config has instapaper_username entry, this is
        updated. Else, self._username is used.
        """
        if self._username or not self.config.get('instapaper_username'):
            self._username = value
        else:
            self.config['instapaper_username'] = value
    @property
    def password(self):
        """ Password property. Returns self._password if set, otherwise config['instapaper_password']. """
        return self._password if self._password is not None else self.config.get('instapaper_password', '')
    @password.setter
    def password(self, value):
        """ Set password.
        If self._password has previously been set (e.g. on instantiation),
        self._password is set. Else if config has instapaper_password entry, this is
        updated. Else, self._password is used.
        """
        if self._password or not self.config.get('instapaper_password'):
            self._password = value
        else:
            self.config['instapaper_password'] = value

    @property
    def headers(self):
        """ Return session headers. """
        return self.session.headers
    @property
    def cookies(self):
        """ Return session cookies. """
        return self.session.cookies
    @property
    def cookies_filepath(self):
        """ Returns cookie_filepath entry from config. """
        path = self.config.get('cookies_filepath')
        if path:
            return os.path.expanduser(os.path.normpath(path))
    @cookies_filepath.setter
    def cookies_filepath(self, cookies_filepath):
        """ Sets cookie_filepath entry in config. (ONLY if cookies_filepath has a non-null value). """
        if cookies_filepath:
            self.config['cookies_filepath'] = cookies_filepath

    def save_cookies(self, filepath=None):
        """ Saves session cookies """
        filepath = filepath or self.cookies_filepath
        if not filepath:
            logger.error("Could not save cookies, filepath/<type> is %s/%s", filepath, type(filepath))
            return
        filepath = os.path.expanduser(filepath)
        logger.info("Saving cookies to file: %s", filepath)
        try:
            with open(filepath, 'wb') as fd:
                save_cookies(fd, self.cookies)
            self.cookies_filepath = filepath
        except FileNotFoundError:
            logger.error("Could not save cookies to file: %s", filepath)

    def load_cookies(self, filepath=None):
        """ Saves session cookies """
        filepath = filepath or self.cookies_filepath
        if not filepath:
            logger.warning("Could not save cookies, filepath/<type> is %s/%s", filepath, type(filepath))
            return
        filepath = os.path.expanduser(filepath)
        logger.info("Loading cookies from file: %s", filepath)
        try:
            with open(filepath, 'rb') as fd:
                cookiejar = load_cookies(fd)
                try:
                    self.cookies.update(cookiejar)
                except AttributeError:
                    # self.cookie does not support update, it might be a http.cookiejar.CookieJar object
                    self.cookies = cookiejar
            self.cookies_filepath = filepath
        except FileNotFoundError:
            logger.error("Could not load cookies from file: %s", filepath)

    def save_config(self, filepath=None):
        """
        Saves config to filepath. If config_filepath is given, this is considered
        the new config location and the config will be saved to this file.
        """
        if filepath is None:
            filepath = self.config_filepath
        try:
            save_config(self.config, filepath)
        except FileNotFoundError:
            logger.error("Could not save config to file: %s", filepath)
        self.config_filepath = filepath

    def load_config(self, filepath=None):
        """ Load config from file. """
        if filepath is None:
            filepath = self.config_filepath
        try:
            config = load_config(filepath)
        except FileNotFoundError:
            logger.error("Could not load config from file: %s", filepath)
        self.config.update(config)
        self.config_filepath = filepath
        return config


    def get_resource_url(self, resource):
        """ Get absolute url for a named resource. """
        return urljoin(self.apiurl, resource)


    def login(self, username, password='', persist_tokens=None):
        """
        Log in with username and your optional password.
        Returns a pair of access tokens (token+secret) on success.
        Returns False if login failed.
        """
        url = self.get_resource_url('oauth/access_token')
        if not username:
            print("No username provided, will not attempt login..")
            return
        tokens = self.session.request_access_tokens(url, username, password)
        if not tokens:
            return False
        userinfo = self.verify_credentials()
        if not userinfo:
            return False
        self.access_tokens = tokens
        if persist_tokens is None:
            persist_tokens = self.config.get('persist_access_tokens') or bool(self.config.get('access_tokens'))
        if persist_tokens:
            self.config['access_tokens'] = tokens
        return tokens



    def verify_credentials(self):
        """
        Returns the currently logged in user.
        Output on success: A user object, e.g.
            [{"type":"user","user_id":54321,"username":"TestUserOMGLOL"}]
        """
        r = self.post('account/verify_credentials')
        try:
            # r.json() has keys "user_id" and "username".
            userinfo = r.json()
            self.status = userinfo[0]["type"] == 'user' and 'username' in userinfo[0]
            self.username = userinfo[0]["username"]
        except (ValueError, IndexError, KeyError):
            print("Userinfo did not produce expected result:", r.text)
            return False
        return userinfo


    def update_access_tokens(self, tokens):
        """
        Update the XAuthSession with this pair of access tokens.
        Tokens must be a dict.
        """
        # This is done automatically by XAuthSession.request_access_tokens:
        self.session._populate_attributes(tokens) # pylint: disable=W0212


    def clear_access_tokens(self):
        """ Removes access tokens from config and saves it. """
        del self.config['access_tokens']
        self.save_config()


    def post(self, endpoint, data=None):
        """
        Post data to REST endpoint.
        Instapaper specifies that parameters are never sent in the query string.
        """
        url = self.get_resource_url(endpoint)
        return self.session.post(url, data=data)


    def check_response(self, response, json=True):
        """
        Check whether response is ok and return it.
        """
        err = is_error(response)
        if err:
            logger.info("Error response: %s", response)
            logger.info("Response status_code: %s, text: %s", response.status_code, response.text[0:1000])
            self.status = False
            # Should probably raise an error or something here...
        else:
            logger.debug("Response OK: Status code: %s", response.status_code)
            self.status = True
        if json:
            return response.json()
        else:
            return response


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
        data = {k: v for k, v in data.items() if v is not None}
        r = self.post('bookmarks/list', data=data)
        return self.check_response(r)


    def add_bookmark(self, url=None, title=None, description=None, folder_id=None,
                     resolve_final_url=1, content=None, is_private_from_source=None):
        """
        Add a bookmark.
        Returns:
            On success: a list with one dict describing the added bookmark. (json parsed)
            On API err: a list with one dict describing the error.
        Uh... If parameters are passed in the body as a urlencoded line.. How do I pass the content?
        - should the content be escaped in any way?
        Input parameters:
            url: Required, except when using private sources (see below).
            title: Optional. If omitted or empty, the title will be looked up by Instapaper synchronously. This will delay the action, so please specify the title if you have it.
            description: Optional. A brief, plaintext description or summary of the article. Twitter clients often put the source tweet's text here, and Instapaper's bookmarklet puts the selected text here if the user has selected any.
            folder_id: Optional. The integer folder ID as returned by the folder/list method described below.
            resolve_final_url: Optional, default 1. Specify 1 if the url might not be the final URL that a browser would resolve when fetching it, such as if it's a shortened URL, it's a URL from an RSS feed that might be proxied
            content: The full HTML content of the page, or just the <body> node's content if possible. Must be utf-8.
            is_private_from_source: A short description label of the source of the private bookmark, such as "email" or "MyNotebook Pro".
        """
        if url is None and not is_private_from_source:
            raise ValueError("No url privided; url must be given for non-private sources.")
        data = {'url': url, 'title': title, 'description': description,
                'folder_id': folder_id, 'resolve_final_url': resolve_final_url,
                'content': content, 'is_private_from_source': is_private_from_source}
        data = {k: v for k, v in data.items() if v is not None}
        r = self.post('bookmarks/add', data=data)
        return self.check_response(r)

    def delete_bookmark(self, bookmark_id):
        """ Delete bookmark by id. """
        logger.info("Deleting bookmark with id: %s", bookmark_id)
        r = self.post('bookmarks/delete', data={'bookmark_id': bookmark_id})
        ret = self.check_response(r)
        if ret == []:
            logger.debug("Bookmark successfully deleted: %s", bookmark_id)
        else:
            logger.info("Bookmark deletion (%s) did not succeed: %s", bookmark_id, r.json())

    def star_bookmark(self, bookmark_id):
        """ Star bookmark by id. """
        r = self.post('bookmarks/star', data={'bookmark_id': bookmark_id})
        return self.check_response(r)

    def archive_bookmark(self, bookmark_id):
        """ Archive bookmark by id. """
        r = self.post('bookmarks/archive', data={'bookmark_id': bookmark_id})
        return self.check_response(r)

    def unarchive_bookmark(self, bookmark_id):
        """ Un-archive bookmark by id. """
        r = self.post('bookmarks/unarchive', data={'bookmark_id': bookmark_id})
        return self.check_response(r)

    def move_bookmark(self, bookmark_id, folder_id):
        """ Move bookmark with bookmark_id to folder with folder_id. """
        r = self.post('bookmarks/move', data={'bookmark_id': bookmark_id, 'folder_id': folder_id})
        return self.check_response(r)

    def get_bookmark_text(self, bookmark_id):
        """ Get text for bookmark with bookmark_id. """
        r = self.post('bookmarks/get_text', data={'bookmark_id': bookmark_id})
        return self.check_response(r)




    ######################
    ##  Folder methods  ##
    ######################

    def list_folders(self):
        """ List all folders. """
        r = self.post('folders/list')
        return self.check_response(r)

    def add_folder(self, title):
        """ Add folder with title <title> """
        r = self.post('folders/add', data={'title': title})
        return self.check_response(r)

    def delete_folder(self, folder_id):
        """ Delete folder with folder_id """
        r = self.post('folders/delete', data={'folder_id': folder_id})
        return self.check_response(r)

    def set_folder_order(self, order):
        """ Set the sort order of folders. """
        r = self.post('folders/set_order', data={'order': order})
        return self.check_response(r)



    #########################
    ##  Highlight methods  ##
    #########################

    def bookmark_highlights(self, bookmark_id):
        """ Return highlights for bookmark with id <bookmark_id> """
        r = self.post('bookmarks/%d/highlights' % bookmark_id)
        return self.check_response(r)

    def bookmark_highlight(self, bookmark_id, text, position):
        """
        Create highlight for bookmark with id <bookmark_id>,
        adding text at position.
        """
        r = self.post('bookmarks/%d/highlight' % bookmark_id,
                      data={'text': text, 'position': position})
        return self.check_response(r)

    def delete_highlight(self, highlight_id):
        """ Delete highlight with id <highlight_id> """
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
    """
    Ensure that value is a string.
    If value is a list/set/tuple, then return a string where each element
    is joined by the given delimiter.
    """
    if value and isinstance(value, (list, set, tuple)):
        value = delimiter.join(value)
    return value
