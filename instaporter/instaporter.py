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
import re
import requests
import argparse
from urllib.parse import urljoin#, urlsplit
from six import string_types
import logging
logger = logging.getLogger(__name__)
from warnings import warn

try:
    from ezfetcher.pdffetcher import fetch_pdf
    from ezfetcher.ezclient import EzClient
    from ezfetcher.utils import load_config as ez_load_config
except ImportError as e:
    warn(e)
    warn("instaporter.instaporter: Could not import ezfetcher library; ezclient will not be available.")


from .instapaper import InstapaperClient
from .utils import init_logging, credentials_prompt, load_consumer_keys, get_config#, load_config, save_config
from .html_utils import make_urls_absolute, html_symbol_repl, get_doc_title

LIBDIR = os.path.dirname(os.path.realpath(__file__))


#from html.parser import HTMLParser
#
#class HTMLBodyCatcher(HTMLParser):
#    """
#    Alternatively, use lxml module:
#        http://lxml.de/parsing.html#parsing-html
#        http://lxml.de/lxmlhtml.html
#
#    """
#    pass



def get_body_innerhtml(html):
    """
    Returns document.body.innerHTML.
    The implementation is currently rather crude, relying soly on a single regex.
    Returns None if no match is found.
    """
    match = re.search("<body ?.*?>(.*)</body>", html, flags=re.DOTALL+re.IGNORECASE)
    if match:
        innerhtml = match.group(1)
        logger.debug("Returning body innerhtml with %s chars.", len(innerhtml))
        return innerhtml
    logger.debug("Regex search did not find any match for body: %s", match)

def transport_files(client, files, args):
    """
    Upload content from files to Instapaper.
    """
    for filepath in files:
        with open(filepath) as fd:
            content = fd.read()
        add_bookmark(client, content, args=args)




def transport_url(instaclient, url, args):
    """
    Download content from url and upload to Instapaper.
    """
    # Session to download content:
    ezclient_config = args.get('ezclient_config')
    ezclient_config_filepath = args.get('ezclient_config_filepath')
    if ezclient_config or ezclient_config_filepath:
        # Use ezfetcher.ezclient.EzClient to download content:
        logger.debug("""Creating ezfetcher.ezclient object to download content;
                     ezclient_config=%s; ezclient_config_filepath=%s""",
                     ezclient_config if isinstance(ezclient_config, string_types) else type(ezclient_config),
                     ezclient_config_filepath)
        """
        Scenarios:
        1) User specifies BOTH ezclient_config and ezclient_config_filepath
        2) User specifies only filepath -> Just use filepath.
        3) User specifies ezclient_config: merged  --> Pass instaporter config to ezclient.
        3) User specifies ezclient_config: default --> Load default ezclient config.
        4) User specifies ezclient_config: <a file path> --> Set ezclient_config_filepath = ezclient_config
        """
        if isinstance(ezclient_config, dict):
            ez_config = ezclient_config
        elif isinstance(ezclient_config, string_types):
            if ezclient_config == "merged":
                ez_config = args
            elif ezclient_config == "default":
                # this together with ez_load_config is only way to get default config.
                ez_config = ez_load_config()
            else:
                if ezclient_config_filepath and ezclient_config:
                    logger.warning("""ezclient_config and ezclient_config_filepath are both specified! \
If ezclient_config is specified together with ezclient_config_filepath,
it must be either a dict, or, if a string, it must be 'merged' or 'default'.""")
                else:
                    ezclient_config_filepath = ezclient_config
        else:
            logger.info("""ezclient_config=%s; ezclient_config_filepath=%s; setting ez_config to None since
it is not a dict or string!""", ezclient_config, ezclient_config_filepath)
            ez_config = None
            #raise ValueError("ezclient_config unrecognized type/value: %s/%s", type(ezclient_config), ezclient_config)
        logger.info("Creating EzClient with config=%s and config_filepath=%s",
                    type(ez_config), ezclient_config_filepath)
        ezclient = EzClient(config=ez_config, config_filepath=ezclient_config_filepath)
        r = ezclient.get(url)
    else:
        logger.info("""ezclient_config or ezclient_config_filepath not specified in config; will use regular \
requests.Session object to download content. (%s, %s)""", ezclient_config, ezclient_config_filepath)
        exit()
        s = requests.Session()
        r = s.get(url)
    html = r.text
    title = get_doc_title(html)
    # If innerhtml is None, provide the full html document.
    content = get_body_innerhtml(html) or html
    # FIXED: Get body.innerHTML.
    # FIXED: Rewrite all hrefs to absolute instead of relative URLs + nature's symbol replacement:
    # Fixed: Add title.
    content = html_symbol_repl(content, url)    # Do this *before* converting URLs.
    content = make_urls_absolute(url, content)
    #with open(os.path.expanduser('~\\temp_full.html'), 'w') as fp:
    #    fp.write(content)
    # It seems is_private_from_source needs to be set, otherwise
    # Instapaper will download content from url rather than the content provided by me.
    # Comment out for testing...
    add_bookmark(instaclient, content, title=title, args=args)

    # Download pdf from url as well:
    download_pdf = args.get('download_pdf')
    from urllib.parse import urlparse
    urlstruct = urlparse(url)
    if download_pdf:
        # Provide the response (r=r) to prevent another get request:
        if not hasattr(download_pdf, '__iter__') or urlstruct.netloc in download_pdf:
            # perhaps add: or any(domain in urlstruct.netloc for domain in download_pdf)
            # This would allow you to enable content fetching on top-level urls, e.g. all *.acs.org domains:
            logger.info("Fetching pdf from html response from %s", r.url)
            # Note: Should args be ezclient_config? Or the Instaporter args/config?
            fetch_pdf(r.url, args, ezclient, r=r)
        else:
            logger.info("download_pdf is specified and iterable, but url.netloc is not in download_pdf. (%s not in %s)",
                        urlstruct.netloc, download_pdf)



def add_bookmark(client, content, title=None, description=None, args=None):
    """ Add bookmark wrapper. """
    is_private_from_source = "Scientific journal"
    kwargs = {'is_private_from_source': is_private_from_source,
              #'url': url,
              'title': title or args.get('title'),
              'description': description or args.get('description'),
              'resolve_final_url': 0,
              'content': content}
    print("Adding bookmark:")
    bookmark = client.add_bookmark(**kwargs)
    print("Bookmark added:\n", bookmark)




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
    parser.add_argument('--configfile', help="Load this config file.")
    parser.add_argument('--instapaper_consumer_keys_file', help="Instapaper client/consumer API key and secret.")
    parser.add_argument('--persist_access_tokens', action="store_true", default=None,
                        help="Persist Instapaper API access token after successfull login.")

    parser.add_argument('--download_pdf', action="store_true", default=None,
                        help="Attempt to download pdf from web page (in addition to storing as Instapaper bookmark).")

    # testing and logging config:
    parser.add_argument('--loglevel', help="Logging level.")
    parser.add_argument('--testing', action="store_true", help="Enable testing mode.")

    subparsers = parser.add_subparsers(dest='command')

    urlcommand = subparsers.add_parser('url', help="Download content from URL.")
    urlcommand.add_argument('url', help="The URL to download pdf from.")

    filecommand = subparsers.add_parser('file', help="Read html content from this/these file(s).")
    filecommand.add_argument('file', help="The URL to download pdf from.")

    testcommand = subparsers.add_parser('test', help="Test mode.")

    return parser


def main(args=None):
    """ Script main function. """
    if args is None:
        ap = get_argparser()
        argns = ap.parse_args()
        args = argns.__dict__
    cmd = args.pop('command')
    if cmd == 'url':
        url = args.pop('url')
    elif cmd == 'test':
        pass
    elif cmd == 'file':
        files = args.pop('file')

    # Init logging. If you want to have logging for config loading, this must be set before doing that.
    # OTOH, if you want to configure logging in the config, you must init logging *after* loading.
    print("args: (before config load)", args)
    init_logging(args)

    # Load config, keys, credentials, etc:
    config_filepath = args.pop('configfile', None)
    config = get_config(args, config_filepath)
    del args

    print("config (after load):", config)

    username = config.get('instapaper_username', '')
    password = config.get('instapaper_password')
    if not (config.get('instapaper_login_prompt') == "as-needed" and config.get('access_tokens')):
        print("Using existing access tokens from config...")
    elif password is None or not username or config.get('instapaper_login_prompt') in ('always', ):
        username, password = credentials_prompt(username)
    consumer_keys = load_consumer_keys(config.get('instapaper_consumer_keys_file'))
    consumer_key = consumer_keys['consumer_key']
    consumer_secret = consumer_keys['consumer_secret']
    #headers = config.get('headers') # InstaClient will update 'headers' in config.

    # Insta client to upload content:
    client = InstapaperClient(config, consumer_key, consumer_secret, username, password,
                              config_filepath=config_filepath)

    if cmd == 'url':
        transport_url(client, url, config)
        #print("config (after load):", config)
    elif cmd == 'test':
        pass
    elif cmd == 'file':
        transport_files(client, files, config)
    else:
        print("Command not recognized...!?")




if __name__ == '__main__':
    main()
