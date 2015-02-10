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


"""
Instaporter: Transport content to Instapaper.

Module to retrieve html content from url and upload it to Instapaper.

REST API doc: www.instapaper.com/api/full



"""


import os
import requests
import yaml
import argparse
import getpass
from urllib.parse import urljoin, urlsplit

from instapaper import InstapaperClient


def credentials_prompt(user='', password=''):
    if not user:
        user = getpass.getuser()
    user = input("User: [%s]" % user) or user
    password = getpass.getpass() or password
    return user, password






def load_config(filepath=None):
    """ Load config from filesystem. """
    if filepath is None:
        filepath = os.path.expanduser("~/.ezfetcher.yaml")
    try:
        return yaml.load(open(filepath))
    except FileNotFoundError:
        return {}

def save_config(config, filepath=None):
    """ Load config from filesystem. """
    if filepath is None:
        filepath = os.path.expanduser("~/.instaporter.yaml")
    try:
        return yaml.dump(config, open(filepath))
    except FileNotFoundError:
        return {}


def get_config(args=None):
    """ Get config, merging args with persistent config. """
    config = load_config()
    if isinstance(argns, argparse.Namespace):
        args = argns.__dict__
    for key, value in args:
        if value is not None:
            config[key] = value
    return config



def get_argparser():
    """ Get argument parser. """
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help="The URL to download pdf from.")
    parser.add_argument('--instapaper_username', '-u', help="Instapaper username/email.")
    parser.add_argument('--instapaper_password', '-p', help="Instapaper password, if you have one.")


def main(args):
    url = args.pop('url')
    config = get_config(args)
    username = config.get('instapaper_username', '')
    password = config.get('instapaper_password', '')
    if not username or config.get('login_prompt') in ('always', ):
        username, password = credentials_prompt(username)
    client_key = config['client_key']
    client_secret = config['client_secret']
    headers = config.get(headers)
    client = InstapaperClient(config, client_key, client_secret, username, password, headers)

    s = requests.Session()
    s.get()



if __name__ == '__main__':
    parser = get_argparser()
    argns = parser.parse_args()
    main(argns)
