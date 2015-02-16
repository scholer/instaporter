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
Test module for html utility module.
"""

import os
import sys

testsdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(testsdir)))

from instaporter.html_utils import html_symbol_repl, get_doc_title #make_urls_absolute


def test_html_symbol_repl():
    """ Simple test. """
    html = """
The sample (5&nbsp;<img src="/__chars/mu/black/med/base/glyph.gif" style="border:0; vertical-align:baseline;"
alt="mu" />l) was deposited on a freshly cleaved mica surface (Ted Pella) and left to adsorb for 5&nbsp;min.
Then 200&nbsp;<img src="/__chars/mu/black/med/base/glyph.gif" style="border:0; vertical-align:baseline;" alt="mu" />l
TAEM buffer of 0.4&nbsp;N&nbsp;m<sup>-1</sup> and a of 10&nbsp;nm.
512&nbsp;<img src="/__chars/math/special/times/black/med/base/glyph.gif" style="border:0; vertical-align:middle;"
alt="times" />&nbsp;512 pixels, <h4 class="norm">Sample preparation for cryo-EM</h4><p class="follows-h4">For
About 25&nbsp;<img src="/__chars/mu/black/med/base/glyph.gif" style="border:0; vertical-align:baseline;" alt="mu" />l of
After adding 5&nbsp;<img src="/__chars/mu/black/med/base/glyph.gif" style="border:0; vertical-align:baseline;"
alt="mu" />l of the. Images were taken on a 4<i>k</i>&nbsp;<img
src="/__chars/math/special/times/black/med/base/glyph.gif" style="border:0; vertical-align:middle;" alt="times" />&nbsp;
<img src="/__chars/math/special/times/black/med/base/glyph.gif" style="border:0; vertical-align:middle;" alt="times" />
with <img src="/__chars/math/special/sim/black/med/base/glyph.gif" style="border:0;
vertical-align:baseline;" alt="approx" />10&#8211;30 class members on average.
<i>q</i> (<i>q</i> = 4<img src="/__chars/pi/black/med/base/glyph.gif" style="border:0; vertical-align:baseline;"
alt="pi" />sin(<i><img src="/__chars/theta/black/ital/base/glyph.gif" style="border:0; vertical-align:middle;"
alt="theta" /></i>)/<i><img src="/__chars/lambda/black/ital/base/glyph.gif" style="border:0; vertical-align:baseline;"
alt="lambda" /></i>, where <i><img src="/__chars/lambda/black/ital/base/glyph.gif" style="border:0;
vertical-align:baseline;" alt="lambda" /></i> is the radiation wavelength and 2<i><img src="/__chars/theta/black/ital/base/glyph.gif"
style="border:0; vertical-align:middle;" alt="theta" /></i> is the scattering angle). low (<img
src="/__chars/math/special/sim/black/med/base/glyph.gif" style="border:0; vertical-align:baseline;"
alt="approx" />0.1&nbsp;mg&nbsp;ml<sup>-1</sup>) and covering 0.004&nbsp;&Aring;<sup>-1</sup>&nbsp;&lt;&nbsp;<i>q</i>
&nbsp;&lt;&nbsp;0.21&nbsp;&Aring;<sup>-1</sup>.
<i><img src="/__chars/alpha/black/ital/base/glyph.gif" style="border:0; vertical-align:baseline;" alt="alpha" /></i>
and <i><img src="/__chars/beta/black/ital/base/glyph.gif" style="border:0; vertical-align:baseline;" alt="beta" /></i>
(<img src="/__chars/math/special/lfen/black/med/base/glyph.gif" style="border:0; vertical-align:baseline;"
alt="left fence" /><i>q</i><img src="/__chars/math/special/rfen/black/med/base/glyph.gif" style="border:0;
vertical-align:baseline;" alt="right fence" />), is thus fitted by</p>
<p class="norm"><img src="/nature/journal/v459/n7243/images/nature07971-m1.jpg"/></p>
<p class="norm">where <i>R</i>(<img src="/__chars/math/special/lfen/black/med/base/glyph.gif" style="border:0;
vertical-align:baseline;" alt="left fence" /><i>q</i><img src="/__chars/math/special/rfen/black/med/base/glyph.gif"
style="border:0; vertical-align:baseline;" alt="right fence" />,&nbsp;<i>q</i>) is the resolution, <img
src="/__chars/math/special/lfen/black/med/base/glyph.gif" style="border:0; vertical-align:baseline;"
alt="left fence" /><i>q</i><img src="/__chars/math/special/rfen/black/med/base/glyph.gif" style="border:0;
vertical-align:baseline;" alt="right fence" />. a 60-<img src="/__chars/mu/black/med/base/glyph.gif"
style="border:0; vertical-align:baseline;" alt="mu" />l.
"""
    new = html_symbol_repl(html, url=None)
    print("New HTML:", new, sep='\n')


def test_get_doc_title():
    html = """
<link rel="search" type="application/sru+xml" href="http://www.nature.com.ez.statsbiblioteket.dk:2048/opensearch/request" title="nature.com" />
<title>Self-assembly of a nanoscale DNA box with a
controllable lid : Article : Nature</title>
"""
    title = get_doc_title(html)
    print("title:", title)
    assert title == """Self-assembly of a nanoscale DNA box with a
controllable lid : Article : Nature"""

if __name__ == '__main__':
    test_html_symbol_repl()
    test_get_doc_title()
