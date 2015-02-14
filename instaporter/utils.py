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

# pylint: disable=C0103

"""
Instaporter utility module.


"""


import os
import yaml
import argparse
import getpass
#from six import string_types
import logging
logger = logging.getLogger(__name__)
#from urllib.parse import urljoin, urlsplit


LIBDIR = os.path.dirname(os.path.realpath(__file__))



def credentials_prompt(user='', password=''):
    """ Simple method to prompt for user credentials. """
    if not user:
        user = getpass.getuser()
    user = input("User: [%s]" % user) or user
    password = getpass.getpass() or password
    return user, password



def load_config(filepath=None):
    """ Load config from filesystem. """
    if filepath is None:
        filepath = os.path.expanduser("~/.instaporter.yaml")
    try:
        config = yaml.load(open(filepath))
        logger.debug("Config with %s keys loaded from file: %s", len(config), filepath)
        return config
    except FileNotFoundError:
        logger.debug("Config file not found: %s, returning empty dict...", filepath)
        return {}


def save_config(config, filepath=None):
    """ Load config from filesystem. """
    if filepath is None:
        filepath = os.path.expanduser("~/.instaporter.yaml")
    yaml.dump(config, open(filepath, 'w'))
    logger.debug("Config with %s keys dumped to file: %s", len(config), filepath)


def get_config(args=None, config_fpath=None):
    """ Get config, merging args with persistent config. """
    config = load_config(config_fpath)

    # Inject client/consumer key and secret:

    # Merge with args:
    if isinstance(args, argparse.Namespace):
        args = args.__dict__
    for key, value in args:
        if value is not None:
            config[key] = value
    logger.debug("Returning config merged with args...")
    return config


def load_consumer_keys(path=None):
    """ Load Instapaper client/consumer key and secret. """
    if path is None:
        path = os.path.expanduser("~.instaporter_key_and_secret.yaml")
    if not os.path.isfile(path):
        path = os.path.join(os.path.dirname(LIBDIR), "consumer_key_and_secret.yaml")
    with open(path) as fd:
        keys = yaml.load(fd)
    logger.debug("Client/Consumer API key and secret loaded from file %s", path)
    return keys


def init_logging(args=None, prefix="Instaporter"):
    """
    Set up standard logging system based on values provided by argsns, namely:
    - loglevel
    - logtofile
    - testing
    """

    # Examples of different log formats:
    #logfmt = "%(levelname)s: %(filename)s:%(lineno)s %(funcName)s() > %(message)s"
    #logfmt = "%(levelname)s %(name)s:%(lineno)s %(funcName)s() > %(message)s"
    # loguserfmt = format of log displayed to the user; logfilefmt = format of log messages written to logfile.
    loguserfmt = "%(asctime)s %(levelname)-5s %(name)20s:%(lineno)-4s%(funcName)20s() %(message)s"
    #logfilefmt = '%(asctime)s %(levelname)-6s - %(name)s:%(lineno)s - %(funcName)s() - %(message)s'
    logdatefmt = "%Y%m%d-%H:%M:%S" # "%Y%m%d-%Hh%Mm%Ss" # Nicer for production logging.
    logtimefmt = "%H:%M:%S" # Nicer for output to user in console and testing.
    #logfiledir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logs')
    #if not os.path.exists(logfiledir):
    #    os.mkdir(logfiledir)
    #if argsns.logtofile:
    #    logfilepath = argsns.logtofile
    #else:
    #    logfilenameformat = '{}_testing.log' if getattr(argsns, 'testing', False) else '{}_debug.log'
    #    logfilename = logfilenameformat.format(prefix)
    #    logfilepath = os.path.join(logfiledir, logfilename)
    #logging.root.setLevel(logging.DEBUG)
    #logstreamhandler = logging.StreamHandler()
    #logging.root.addHandler(logstreamhandler)
    #logstreamformatter = logging.Formatter(loguserfmt, logtimefmt)
    #logstreamhandler.setFormatter(logstreamformatter)


    if 'loglevel' in args:
        try:
            loglevel = int(args['loglevel'])
        except ValueError:
            loglevel = getattr(logging, args['loglevel'])
    else:
        loglevel = logging.DEBUG if args.get('testing') else logging.INFO

    logging.basicConfig(level=loglevel,
                        format=loguserfmt,
                        datefmt=logtimefmt if args.get('testing') else logdatefmt,
                        # filename='example.log',
                        )

    logger.info("Logging system initialized with loglevel %s", loglevel)
