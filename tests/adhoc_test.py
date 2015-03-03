#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Rasmus Sorensen, rasmusscholer@gmail.com <scholer.github.io>

# pylint: disable=C0103,C0301,R0913,W0142


"""
Ad-hoc test module.
"""


import os
import sys

import logging
logger = logging.getLogger(__name__)


testsdir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(os.path.dirname(testsdir), "instaporter")
sys.path.insert(0, os.path.join(os.path.dirname(testsdir)))
#sys.path.insert(0, libdir)


from instaporter import instapaper
from instaporter import instaporter
from instaporter import utils

#from .utils import credentials_prompt, load_config, save_config, load_consumer_keys


if __name__ == '__main__':


    args = {'testing': True}
    utils.init_logging(args)

    keys = instaporter.load_consumer_keys()
    client_key, client_secret = (keys[k] for k in ('consumer_key', 'consumer_secret'))
    #username = "rasmusscholer@gmail.com"
    #username, password = instaporter.credentials_prompt(username)

    config = utils.load_config()
    config.setdefault('persist_access_tokens', True)
    config.setdefault('instapaper_login_prompt', True)

    #client = instapaper.InstapaperClient(config, client_key, client_secret, username, password)
    client = instapaper.InstapaperClient(config, client_key, client_secret)

    print("Config:", client.config)
    #sys.exit()

    # Add bookmark by url:
    # client.add_bookmark("https://requests-oauthlib.readthedocs.org/en/latest/") # works!

    # Add bookmark with content:
    def test_add_bookmark_b(client):
        content = open('content2.html').read()
        print("Content length:", len(content))
        url = 'https://dev.twitter.com/oauth/xauth'
        kwargs = {'url': url,
                  'content': content}
        bookmark = client.add_bookmark(**kwargs)
        print("Bookmark added:\n", bookmark)
        # Didn't work, Instapaper read the content from the URL, not the given content.

    def test_add_bookmark_a(client):
        content = "<p>xAuth provides a way for desktop and mobile applications to exchange a username and password for an OAuth access token. Once the access token is retrieved, xAuth-enabled developers should dispose of the login and password corresponding to the user.</p>"
        print("Content length:", len(content))
        url = "https://dev.twitter.com/oauth/pin-based"
        #is_private_from_source = "Scientific journal"
        kwargs = {'url': url,
                  'title': "xAuth vs PIN tets 1",
                  'description': 'First test trying to add content directly.',
                  'resolve_final_url': 0,
                  'content': content}
        print("kwargs:\n", kwargs)
        bookmark = client.add_bookmark(**kwargs)
        print("Bookmark added:\n", bookmark)
        # Result: Didn't work, Instapaper read the content from the URL, not the given content.
        # (although title and description were used from the kwargs!)
        # bookmark_id : 554908138


    def test_add_bookmark_c(client):
        content = "<p>Here is content for another test (test c), trying to upload content manually/directly. This time, url is not specified, but is_private_from_source is.</p>"
        print("Content length:", len(content))
        is_private_from_source = "Scientific journal"
        kwargs = {'is_private_from_source': is_private_from_source,
                  #'url': url,
                  'title': "Content adding test c",
                  'description': 'Third test adding content directly (test c)...',
                  'resolve_final_url': 0,
                  'content': content}
        print("kwargs:\n", kwargs)
        bookmark = client.add_bookmark(**kwargs)
        print("Bookmark added:\n", bookmark)
        # This works!


    def test_delete_bookmark(client):
        bookmark_id = 554908138
        client.delete_bookmark(bookmark_id)
        # Works!


    #test_delete_bookmark(client)   # Worked.
    #test_add_bookmark_c(client)    # Worked.
