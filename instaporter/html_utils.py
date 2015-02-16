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


import logging
logger = logging.getLogger(__name__)


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

    other =[('<img\s[^>]*?src="/__chars/less/special/le/[^>]*>', "&#8804"), # Less-than-or-equal
            ('<img\s[^>]*?src="/__chars/micro/[^>]*>', "&#956"), # Micro (looks similar to mu)
            ('<img\s[^>]*?src="/__chars/plus/special/plusmn/[^>]*>', "&#177"), # Plus-minus
    #        ('<img src="/__chars/math/special/lfen/[^>]*>', "&#9001"), # Left bracket/chevron/fence
    #        ('<img src="/__chars/math/special/rfen/[^>]*>', "&#9002"), # Right bracket/chevron/fence
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
