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
#,R0913,R0914


"""
Various Zotero utility functions and examples.
"""

import logging
logger = logging.getLogger(__name__)
from warnings import warn
import time
from six import string_types
from functools import partial
from copy import deepcopy

try:
    from pyzotero import zotero
except ImportError:
    print("pyzotero / Zotero-Client not found. Please download from github.com/scholer/zotero-client.")


def unicode_print(*args, sep=' '):
    """
    Safely print unicode, avoiding unicode errors on non-unicode
    consoles (e.g. on Windows, sigh).
    """
    try:
        print(*args)
    except UnicodeEncodeError:
        st = sep.join(args)
        st += " (could not print some unicode character)"
        bst = st.encode('utf-8')
        print(bst)
        #sys.stdout.buffer.write(bst)


def add_to_zotero(config, metadata, pdf=None, collections=None, template=None):
    """
    Add reference item to Zotero and attach pdf if given.
    Mandatory argument <metadata> must be a dict with required keys:
        html: dict with html-extracted data, e.g. title and keywords.
        doi:  dict with DOI data (used to create Zotero metadata).
    <metadata> can optionally also have the following keys:
        url:  The url that you want to use for the Zotero 'url' field.
    If collections is not given, config['collection_ids'] is used.
    <template> is the zotero template to use for adding the item.
    If template is not given, it will be obtained automatically.
    """

    if collections is None:
        collections = config.get('collection_ids')

    html_title = metadata['html'].get('title')
    doi_data = metadata['doi'].copy() # zotero_data_from_cls will modify input doi_data
    if not (html_title and html_title.lower() == doi_data.get('title', '').strip(" []<>")):
        print("HTML title is:", html_title)
        unicode_print("DOI title is: ", doi_data['title'].strip(" []<>"))
        ok = input("Continue importing DOI data to Zotero? [yes/no] ")
        ok = bool(ok) and ok[0].lower() == 'y'
        if not ok:
            print("Aborting zotero import...")
            return
    print("HTML and DOI titles accepted, continuing with DOI Zotero import...")

    # Do zotero import:

    # Seems like there are problems with unicode characters?? E.g. 'ø' ??

    zot = zotero.Zotero(config['library_id'], config['library_type'], config['api_key'])
    if template is None:
        # Empty "journalArticle" template:
        template = zot.item_template('journalArticle')
    item_data = zotero_data_from_cls(template, doi_data)
    if not item_data:
        print("Could not obtain item_data, needed in order to add item to Zotero. Aborting...")
        return

    # Add metadata to item_data:
    # Url from DOI resources will usually just be dx.doi.org/... This can always be re-created from the DOI field.
    item_data['url'] = metadata.get('url')
    # Collections for new items: Find collection IDs by browsing zotero.org.
    # insta_col = zot.create_collection([{'name': 'Instapaper'}])
    if collections:
        item_data['collections'] = collections
    if metadata['html'].get('keywords'):
        kwtags = [{'tag': keyword, "type": 1} for keyword in metadata['html']['keywords']]
        # Extend instead of overwrite if item_data alraedy has tags:
        # Or maybe do nothing if item_data already has tags (from DOI query).
        if 'tags' in item_data:
            item_data['tags'].extend(kwtags)
        else:
            item_data['tags'] = kwtags
    if not item_data.get('abstractNote') and metadata['html'].get('abstract'):
        item_data['abstractNote'] = metadata['html'].get('abstract')

    # Add item (payload is just a list of items to add)
    # pdb.set_trace()
    resp = zot.create_items([item_data])
    try:
        key = resp['success']['0']
    except KeyError:
        print("Zotero creation did not succeed: ", resp)
        return
    # Upload pdf
    if pdf:
        # Upload list of pdf files under optional parent item.
        # TODO: Consider attaching pdf as LINKED_FILE rather than imported_file
        # Options are: imported_file,imported_url,linked_file,linked_url
        # A linked_file is what you get if you hold ctrl+shift while drag-dropping a pdf to an item.
        # Linked attachments can use relative paths in a directory that you sync across devices
        # using third party software, e.g. Dropbox.
        att_resp = zot.attachment_simple([pdf], key)
        try:
            att_key = att_resp['success']['0']
            print("Uploaded attachment:", att_key)
        except KeyError:
            print("Zotero creation did not succeed: ", att_resp)




def zotero_data_from_cls(data_template, clsdata):
    """
    Update Zotero API data with CLS formatted data.
    NOTICE: clsdata WILL BE MODIFIED, removing all entries that were moved to to data_template.
    If you do not want this, make a copy and provide that as argument.
    """
    # Mapping DOI data to Zotero item['data']:
    # Refs:
    # * https://www.zotero.org/support/kb/field_mappings - Nah.
    # * http://gsl-nagoya-u.net/http/pub/csl-fields/journalArticle.html
    # * http://gsl-nagoya-u.net/http/pub/citeproc-doc.html
    # * http://aurimasv.github.io/z2csl/typeMap.xml
    # * https://www.zotero.org/support/dev/citation_styles/csl_0.8.1_syntax
    # * http://crosscite.org/cn/
    # Can this be used for anything? https://github.com/dotcs/doimgr

    # "author" -> "creators"  Uh... no, not that simple :\
    item_data = deepcopy(data_template)    # Shallow copy will keep lists to be modified.
    if item_data.get('creators') == [{"creatorType": "author", "firstName": '', "lastName": ''}]:
        # Reset creators:
        logging.debug("Resetting zotero 'creators' field to empty list...")
        item_data['creators'] = []
    else:
        logging.debug("Existing creators: %s", item_data.get('creators'))


    # 1-to-1 mappings: Zotero-field, CLS-field
    # Note: these zotero fields MUST be single values, not lists/arrays
    # (Otherwise you get a HTTP 500 "Internal Server Error" from the server.)
    # DONE: All dates must be strings, not weird dict.
    def str_to_str(clsvalue, key=None):
        """ Return str as str. Optional arg <key> is a DOI input key, and is only used for logging output. """
        if not isinstance(clsvalue, string_types):
            if isinstance(clsvalue, (list, tuple)):
                logger.info("CLS entry (%s: %s) is list, not string."\
                            "Can only use one value; will use the first element.",
                            key, clsvalue)
                # Pick first non-empty value:
                clsvalue = next((val for val in clsvalue if val), clsvalue[0])
            else:
                raise TypeError("CLS value %s has wrong type: %s (should be %s)" % (clsvalue, type(clsvalue), str))
        return clsvalue
    def author_to_creators(clsauthors, key=None, creatortype="author"):
        """ Return creators list. """
        if not clsauthors:
            logger.info("CLS entry '%s' is empty...", key)
        if isinstance(clsauthors, dict):
            clsauthors = [clsauthors]
        creators = [{'creatorType': creatortype,
                     'firstName': author['given'],
                     'lastName': author['family']}
                    for author in clsauthors]
        return creators
    editor_to_creator = partial(author_to_creators, creatortype="editor")
    def date_to_str(clsdate, key=None):
        """
        A cls date is a dict with form {'date-parts': [[2009, 05, 07]], 'timestamp': }
        The timestamp is milli-seconds since the epoch. Can be converted using
            time.gmtime(clsdate['timestamp']/1000) --> time tuple
            time.ctime(clsdate['timestamp']/1000)  --> time string
        The date-parts is a list of lists. It can be converted using:
            datetuple =
        """
        if 'timestamp' in clsdate:
            datetuple = time.gmtime(clsdate['timestamp']/1000)
        else:
            try:
                date_lst = clsdate['date-parts'][0]
                datetuple = tuple(date_lst) + tuple(0 for i in range(9-len(date_lst)))
            except KeyError:
                logger.warning("CLS entry '%s' does not contain 'timestamp' or 'date-parts' keys.", key)
        return time.asctime(datetuple)

    # Mapping: (Zotero-key, CLS/DOI-key, converter-function)
    mapping = (('abstractNote', 'abstract', str_to_str),
               ('accessDate', 'accessed', date_to_str),
               ('archive', 'archive', str_to_str),
               ('archiveLocation', 'archive_location', str_to_str),
               ('callNumber', 'call-number', str_to_str),
               ('creators', 'author', author_to_creators),
               ('creators', 'editor', editor_to_creator),
               ('date', 'issued', date_to_str),
               ('DOI', 'DOI', str_to_str),
               ('extra', 'note', str_to_str),
               ('ISSN', 'ISSN', str_to_str),
               ('issue', 'issue', str_to_str),
               ('journalAbbreviation', 'container-title-short', str_to_str),
               ('language', 'language', str_to_str),
               ('libraryCatalog', 'source', str_to_str),
               ('pages', 'page', str_to_str),
               ('publicationTitle', 'container-title', str_to_str),
               ('series', 'collection-title', str_to_str),
               ('seriesTitle', 'collection-title', str_to_str),
               ('shortTitle', 'title-short', str_to_str),
               ('title', 'title', str_to_str),
               ('url', 'URL', str_to_str),
               ('volume', 'volume', str_to_str))
    cls_keys_not_present = []
    zot_keys_not_in_template = []
    # DONE: Make sure you only use keys that are in the data_template. - Check
    # DONE: Include author and editor in this generic run-through
    # DONE: Making sure all types are correct using converter functions.
    # Unmappable: ('rights', ''), ('seriesText', ''),
    for zotkey, clskey, converter in mapping:
        try:
            clsvalue = clsdata.pop(clskey)
        except KeyError:
            cls_keys_not_present.append(clskey)
        else:
            if zotkey not in item_data:
                zot_keys_not_in_template.append(zotkey)
            else:
                existing_zot_value = item_data[zotkey]
                if isinstance(existing_zot_value, string_types):
                    # Most entries, including all dates
                    item_data[zotkey] = converter(clsvalue, clskey)
                elif isinstance(existing_zot_value, dict):
                    # E.g. "relations"
                    existing_zot_value.update(converter(clsvalue, clskey))
                elif isinstance(existing_zot_value, list):
                    # E.g. tags, collections, creators
                    existing_zot_value.extend(converter(clsvalue, clskey))
                else:
                    warn("Unexpected type for %s: %s (%s)" % \
                         (zotkey, existing_zot_value, type(existing_zot_value)))
    logger.info("CLS keys not found in DOI data: %s", cls_keys_not_present)
    logger.info("Zotero keys not in template: %s", zot_keys_not_in_template)
    return item_data




def zotero_delete_attachments():
    """
    Example function, code from playing around with the Enzymatic library.

    # Get attachment: at = zot.item(key)
    # At size: at['links']['enclosure']['length']/2**20
    # Get all attachments:
    #attachments = zot.items(itemType="attachment", limit=1000) # Default limit is 25!
    #always check zot.links after a call...
    # If an imported attachment does not have 'length' entry, it might be a duplicate;
    # check for an at['relations']['owl:sameAs'] entry.
    # Get total size of all attachments in MB:
    #sum(at['links'].get('enclosure', {}).get('length', 0) for at in attachments
         if "imported_" in at['data']['linkMode'])/2**20
    """
    # Easy way to delete zotero attachments.
    zot = zotero.Zotero() # Add lib type and id plus api_key
    attachments = zot.items(itemType='attachment', limit=1000)
    # Find those that actually consume space:
    # Note: deleting these may leave other attachments that links to these empty!
    bulk = [at for at in attachments if at['links'].get('enclosure', {}).get('length', 0) > 0]
    for it in bulk:
        try:
            print("{:<.02}MB {}".format(it['links']['enclosure']['length']/2**20, it['data']['filename']))
        except UnicodeEncodeError:
            print("{:<.02}MB title={}".format(it['links']['enclosure']['length']/2**20, it['data']['title']))
        answer = input("Delete this file? ")
        answer = answer and answer[0].lower() == 'y'
        if answer:
            zot.delete_item(it)

