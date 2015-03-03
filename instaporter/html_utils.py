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

# pylint: disable=C0103,W0142


"""
Utility functions for rewriting/reformatting/replacing html documents/content.
"""

import re
from urllib.parse import urljoin
import requests

import logging
logger = logging.getLogger(__name__)


def find_doi(html):
    """
    Find a regex in html. If more DOIs are present, we assume the first DOI is the one we want.
    """
    #DOI_REGEX = r"doi.+(10\\.\d{4,6}/[^\"'&<% \t\n\r\f\v]+)"
    DOI_REGEX = r"doi.+(10\.\d{4,6}/[^\"'&<%\s]+)"
    hits = re.findall(DOI_REGEX, html)
    if hits:
        return hits[0]
    return None

def find_headings(html):
    """
    Find headings in html.
    Returns a list of (<heading-level>, <heading>), e.g. [(2, "Abstract")]
    """
    # \1 refers to the first group.
    # (?P=name) refers to the named groups with name "name".
    # (?...) specifies a non-capturing group.
    headings = re.findall(r"<h(\d)[^>]*?>(?P<heading>.*?):?</h\1>", html)
    return headings

def find_titles(html):
    """
    Find title tags in html.
    """
    titles = re.findall(r"<title[^>]*?>(.*?)</title>", html)
    return titles

def find_keywords(html):
    """
    Find tags/keywords in html.
    Uhm... Doesn't seem to be that easy.
    Nature has this: <meta name="keywords" content="Long non-coding RNAs" />
    .. same for ACS Journals.
    """
    # TODO: Find keywords/tags, better.
    tags = re.findall(r'<meta\s(\w+="[^"]+")\s+(\w+="[^"]+")[^>]*?>', html)
    tags = [tag for tag in tags if any(elem.lower() == 'name="keywords"' for elem in tag)]
    if not tags:
        return
    tag = tags[0]
    keywords = tag[1] if tag[0] == 'name="keywords"' else tag[0]
    keywords = keywords.split("=")[1].strip(' "')
    keywords = [word.strip() for word in keywords.split(',')]
    return keywords

def find_metadata(html, url=None):
    """
    Find as much metadata from html as possible.
    Returns a construct, metadata, with:
        html:
            title: title, as found in html.
            keywords: keywords, as found in html.
            abstract: abstract, as found in html.
        doi: <CLS data from dx.doi.org, if a DOI was found in the html>
    """
    metadata = {'doi': None, 'url': url}
    html_titles = find_titles(html)
    doi = find_doi(html)
    metadata['html'] = {'title': html_titles[0] if html_titles else None,
                        'keywords': find_keywords(html),
                        'abstract': '',
                        'doi': doi}
    #html_keywords = find_keywords(html)
    #html_abstract = ''
    if not doi:
        print("\nCould not find any DOI in html; aborting..")
    else:
        doi_data = get_doi_data(doi)
        if doi_data:
            metadata['doi'] = doi_data
    return metadata

def get_doi_data(doi):
    """ Get DOI data as dict. Returns None if DOI response was not ok. """
    r = get_doi_response(doi)
    if not r.ok:
        print("DOI response not OK: ", r)
        return
    return r.json()

def get_doi_response(doi):
    """ Query dx.doi.org for doi. Return requests Response. """
    # Do NOT include the ":" in the headers for requests:
    doi_headers = {"Accept": "application/vnd.citationstyles.csl+json"}
    doi_api_baseurl = "http://dx.doi.org"
    doi_endpoint = urljoin(doi_api_baseurl, doi)
    r = requests.get(doi_endpoint, headers=doi_headers)
    return r


def get_doc_title(html):
    """
    Get title of html document.
    """
    regex = r'<title>(.*?)</title>'
    match = re.search(regex, html, flags=re.DOTALL)
    if match:
        title = match.group(1)
    return title


def make_urls_absolute(baseurl, html):
    """
    Ensure that all urls in html document is absolute, not relative.
    Consideration: Should you rewrite url fragments ?
        Why not:
          - It would be nice to use fragment/anchors in the text for navigation.
        Why rewrite anyways:
          - Many fragments are provided as divs with an id="<id>" attribute.
            Since the divs are completely stripped, the fragment is lost, and any anchors wouldn't work.
    """
    # Replace href=:
    tot = 0
    fmt = None
    for tag in ('href', 'src'):
        fmt = tag + '="%s"' # e.g. 'href="%s"'
        repl = lambda match: fmt % urljoin(baseurl, match.group(1))
        (html, n) = re.subn(tag+'="([^"]*?)"', repl, html, flags=re.MULTILINE) # e.g. 'href="([^"]*?)"'
        tot += n
    #repl = lambda match: 'href="%s"' % urljoin(baseurl, match.group(1))
    #(html, n) = re.subn('href="([^"]*?)"', repl, html)
    #tot += n
    ## Replace src=:
    #repl = lambda match: 'src="%s"' % urljoin(baseurl, match.group(1))
    #(html, n) = re.subn('src="([^"]*?)"', repl, html)
    #tot += n
    logger.info("%s link/href/src replaced in content.", tot)
    return html


def html_symbol_repl(html, url=None):
    """
    Make replacements in html (currently hardcoded, because...)
    """

    symbols = """alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi
              omicron pi rho sigma tau upsilon phi chi psi omega""".split()
    greek = [(r'<img\s[^>]*?src="/__chars/%s/[^>]*>' % char, "&#%s;" % code)
             for code, char in enumerate(symbols, 945)]
    #replacements = [('<img src="/__chars/alpha/[^>]*>', "&#945;"), # Greek mu = micro symbol
    #                ('<img src="/__chars/mu/[^>]*>', "&#956;"), # Greek mu = micro symbol
    #                ('<img src="/__chars/beta/[^>]*>', "&#956;"), # Greek mu = micro symbol
    #                ('<img src="/__chars/mu/[^>]*>', "&#956;"), # Greek mu = micro symbol
    #math = [('<img src="/__chars/math/special/times/[^>]*>', "&#215"), # Times/multiplication
    #        ('<img src="/__chars/math/special/sim/[^>]*>', "&#126"), # Tilde/similarity
    #        ('<img src="/__chars/math/special/plusmn/[^>]*>', "&#177"), # Plus-minus
    #        ('<img src="/__chars/math/special/lfen/[^>]*>', "&#9001"), # Left bracket/chevron/fence
    #        ('<img src="/__chars/math/special/rfen/[^>]*>', "&#9002"), # Right bracket/chevron/fence
    #       ]
#lt      66
#gt      68
#    symbols = """
#sim     126
#plusmn  177
#times   215
#lfen    9001
#rfen    9002"""
    symbols = (("sim", 126), ("plusmn", 177), ("times", 215), ("lfen", 9001), ("rfen", 9002))
    math = [(r'<img\s[^>]*?src="/__chars/math/special/%s/[^>]*>' % char, "&#%s;" % code)
            for char, code in symbols]

    other = [(r'<img\s[^>]*?src="/__chars/less/special/le/[^>]*>', "&#8804"), # Less-than-or-equal
             (r'<img\s[^>]*?src="/__chars/micro/[^>]*>', "&#956"), # Micro (looks similar to mu)
             (r'<img\s[^>]*?src="/__chars/plus/special/plusmn/[^>]*>', "&#177"), # Plus-minus
             #(r'<img src="/__chars/math/special/lfen/[^>]*>', "&#9001"), # Left bracket/chevron/fence
             #(r'<img src="/__chars/math/special/rfen/[^>]*>', "&#9002"), # Right bracket/chevron/fence
            ]
    #le      8804

    replace = greek + math + other
    tot = 0
    repl = None
    for regex, rep in replace:
        repl = lambda match: rep
        (html, n) = re.subn(regex, repl, html, flags=re.MULTILINE+re.DOTALL)
        tot += n
    unrecognized = 'src="/__chars'
    logger.info("%s symbols replaced (another %s possible symbols not recognized) in html from %s",
                tot, html.count(unrecognized), url)
    print("%s symbols replaced (another %s possible symbols not recognized) in html from %s" \
          %(tot, html.count(unrecognized), url))
    return html
