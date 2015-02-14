#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2014-2015 Rasmus Sorensen, rasmusscholer@gmail.com <scholer.github.io>

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

# pylint: disable=C0103,W0142

"""
Instaporter: Transport content to Instapaper.

Module to retrieve html content from url and upload it to Instapaper.

REST API doc: www.instapaper.com/api/full



"""


import os
import requests
import argparse
#from urllib.parse import urljoin, urlsplit
#from six import string_types
import logging
logger = logging.getLogger(__name__)

from .instapaper import InstapaperClient
from .utils import credentials_prompt, load_consumer_keys, get_config#, load_config, save_config

LIBDIR = os.path.dirname(os.path.realpath(__file__))





def get_argparser():
    """
    Get argument parser.
    Config parameters:
        apiurl : Base api url, defaults to 'https://www.instapaper.com/api/1.1/'
        access_tokens : saved access tokens.
        persist_access_tokens : persist access tokens in config (only applies if config has no 'access_tokens' already.)
        instapaper_username : Your Instapaper username/email.
        instapaper_password : Your (optional) Instapaper password.
        instapaper_login_prompt : allow the program to query the user for credentials as-needed.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--instapaper_username', '-u', help="Instapaper username/email.")
    parser.add_argument('--instapaper_password', '-p', help="Instapaper password, if you have one.")

    subparsers = parser.add_subparsers(dest='command')

    urlcommand = subparsers.add_parser('url', help="Download content from URL.")
    urlcommand.add_argument('url', help="The URL to download pdf from.")

    filecommand = subparsers.add_parser('file', help="Read content from this file.")
    filecommand.add_argument('file', help="The URL to download pdf from.")

    testcommand = subparsers.add_parser('test', help="Read content from this file.")

    return parser


def main(args):
    """ Script main function. """
    cmd = args.pop('command')
    if cmd == 'url':
        url = args.pop('url')
    elif cmd == 'test':
        pass
    elif cmd == 'file':
        files = args.pop('file')

    # Load config, keys, credentials, etc:
    config = get_config(args)
    username = config.get('instapaper_username', '')
    password = config.get('instapaper_password')
    if not (config.get('instapaper_login_prompt') == "as-needed" and config.get('access_tokens')):
        print("Using existing access tokens from config...")
    if password is None or not username or config.get('instapaper_login_prompt') in ('always', ):
        username, password = credentials_prompt(username)
    consumer_keys = load_consumer_keys()
    consumer_key = consumer_keys['consumer_key']
    consumer_secret = consumer_keys['consumer_secret']
    headers = config.get('headers')

    # Insta client to upload content:
    client = InstapaperClient(config, consumer_key, consumer_secret, username, password, headers)


    if cmd == 'url':
        transport_url(client, url, args)
    elif cmd == 'test':
        pass
    elif cmd == 'file':
        transport_files(client, files, args)
    else:
        print("Command not recognized...!?")


def transport_files(client, files, args):
    """
    Upload content from files to Instapaper.
    """
    for filepath in files:
        with open(filepath) as fd:
            content = fd.read()
        add_bookmark(client, content, args)


def transport_url(client, url, args):
    """
    Download content from url and upload to Instapaper.
    """
    # Session to download content:
    s = requests.Session()
    r = s.get(url)
    html = r.text
    # TODO: Extract body from html
    content = html
    # It seems is_private_from_source needs to be set, otherwise
    # Instapaper will download content from url rather than the content provided by me.
    add_bookmark(client, content, args)


def add_bookmark(client, content, args):
    """ Add bookmark wrapper. """
    is_private_from_source = "Scientific journal"
    kwargs = {'is_private_from_source': is_private_from_source,
              #'url': url,
              'title': args.get('title'),
              'description': args.get('description'),
              'resolve_final_url': 0,
              'content': content}
    print("Adding bookmark:")
    bookmark = client.add_bookmark(**kwargs)
    print("Bookmark added:\n", bookmark)




def test(argns):
    """ Simple test function. """
    pass


if __name__ == '__main__':
    ap = get_argparser()
    argns = ap.parse_args()
    main(argns)
