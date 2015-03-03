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


import yaml


from instaporter.zotero_utils import add_to_zotero, zotero_data_from_cls




def test_zotero_data_from_cls():
    doi_data = yaml.load("""
DOI: 10.1038/nature14228
ISSN: [0028-0836, 1476-4687]
URL: http://dx.doi.org/10.1038/nature14228
abstract: Inflammation promotes regeneration of injured tissues through (...)
author:
- {family: Taniguchi, given: Koji}
- {family: Wu, given: Li-Wha}
- {family: Grivennikov, given: Sergei I.}
- {family: de Jong, given: Petrus R.}
editor:
- {family: Zucman-Rossi, given: Jessica}
- {family: Guan, given: Kun-Liang}
- {family: Karin, given: Michael}
container-title: Nature
deposited:
  date-parts:
  - [2015, 2, 24]
  timestamp: 1424736000000
indexed:
  date-parts:
  - [2015, 2, 27]
  timestamp: 1424997590082
issue: '7082'
issued:
  date-parts:
  - [2015, 2, 25]
member: http://id.crossref.org/member/339
page: 297-302
prefix: http://id.crossref.org/prefix/10.1038
publisher: Nature Publishing Group
reference-count: 60
score: 1.0
source: CrossRef
subject: [General]
subtitle: []
title: "A gp130\u2013Src\u2013YAP module links inflammation to epithelial regeneration"
type: journal-article
volume: '440'
""")
    empty = yaml.load("""
DOI: ''
ISSN: ''
abstractNote: ''
accessDate: ''
archive: ''
archiveLocation: ''
callNumber: ''
collections: []
creators:
- {creatorType: author, firstName: '', lastName: ''}
date: ''
extra: ''
issue: ''
itemType: journalArticle
journalAbbreviation: ''
language: ''
libraryCatalog: ''
pages: ''
publicationTitle: ''
relations: {}
rights: ''
series: ''
seriesText: ''
seriesTitle: ''
shortTitle: ''
tags: []
title: ''
url: ''
volume: ''
""")
    zot_data = yaml.load("""
DOI: 10.1038/nature14228
ISSN: 0028-0836
abstractNote: Inflammation promotes regeneration of injured tissues through (...)
accessDate: ''
archive: ''
archiveLocation: ''
callNumber: ''
collections: []
creators:
- {creatorType: author, firstName: Koji, lastName: Taniguchi}
- {creatorType: author, firstName: Li-Wha, lastName: Wu}
- {creatorType: author, firstName: Sergei I., lastName: Grivennikov}
- {creatorType: author, firstName: Petrus R., lastName: de Jong}
- {creatorType: editor, firstName: Jessica, lastName: Zucman-Rossi}
- {creatorType: editor, firstName: Kun-Liang, lastName: Guan}
- {creatorType: editor, firstName: Michael, lastName: Karin}
date: Mon Feb 25 00:00:00 2015
extra: ''
issue: '7082'
itemType: journalArticle
journalAbbreviation: ''
language: ''
libraryCatalog: CrossRef
pages: '297-302'
publicationTitle: Nature
relations: {}
rights: ''
series: ''
seriesText: ''
seriesTitle: ''
shortTitle: ''
tags: []
title: "A gp130\u2013Src\u2013YAP module links inflammation to epithelial regeneration"
url: http://dx.doi.org/10.1038/nature14228
volume: '440'
""")
    assert zotero_data_from_cls(empty, doi_data) == zot_data
    #print("hej")
