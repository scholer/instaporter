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

# pylint: disable=C0301

"""

Module for creating a requests.Session object that implements
the xauth workflow for oauth1 communication with a server.

This is based on Kenneth Reitz' requests-oauthlib,
which combines requests lib with oauthlib.

Unfortunately, this doesn't support the xAuth workflow, hence this module.


Note:
* Using xAuth should be fairly simple.
* I imagine if I just combine oauthlib with requests, then it is pretty much it.

About Instapaper's API:
* www.instapaper.com/api/full
* Similar to twitters xauth, see e.g. dev.twitter.com/oauth/xauth
* HMAC-SHA1 signature, HTTPS for all endpoints
* All requests made via POST
* All parameters (except OAuth/xAuth parameters) are passed in the request-body (not query string).
* The OAuth parameters should be passed in the Authorization: header, not in the query-string or request-body.
* (Parameters can be provided by three means in a HTTP request: query, header and body)

Instapaper - XAuth details:
* Is Oauth 1.0a, as far as I can tell (from various posts)..
* xAuth - no request-token/authorize workflow. Requests must still be signed, but getting a token is simple.
*

What's the difference between xAuth vs OAuth1 vs OAuth2 vs other e.g. BasicAuth?
* xAuth does not require a browser session/popup.
* xAuth is basically OAuth but without the need for the user to confirm the app in their twitter account. Basically the simplest form of OAuth.
* stackoverflow.com/questions/3324238/what-is-the-difference-among-basicauth-oauth-and-xauth
* dev.twitter.com/oauth/xauth
* - "xAuth allows desktop and mobile applications to skip the request_token and authorize steps and jump right to the access_token step."
* OAuth1 vs OAuth2: All cryptographic steps were moved to server side in OAuth 2.

xAuth examples and threads:
* Using rauth oauth2 lib ("rauth"):
* - stackoverflow.com/questions/19621894/connecting-to-vimeo-with-xauth-in-python
* Using simplegeo's python-oauth2 ("oauth2"):
* - stackoverflow.com/questions/5503260/xauth-using-python-oauth2
* - code.larlet.fr/django-oauth-plus/wiki/consumer_xauth_example
* - gist.github.com/codingjester/3497868 (oauth2 + urllib)
* - gist.github.com/ken8203/9724878 (oauth2 + urllib)
* Using Kenneth's requests-oauthlib:
* - docs.python-requests.org/en/latest/user/authentication/
* - OAuth1 workflow: requests-oauthlib.readthedocs.org/en/latest/oauth1_workflow.html
* Using just requests (and doing signing by it self):
* - github.com/malthe/requests-xauth/
* Twitter xAuth example (python, uses oauth2 + urllib)
* - github.com/yuitest/twitterxauth
* - This is basically copy/paste of one of the stackoverflow threads.
* Twitter:
* - dev.twitter.com/oauth/overview/single-user (advices the use of simplegeo's oauth2)
* Urbanesia:
* - pypi.python.org/pypi/oauthnesia, github.com/Urbanesia/oauthnesia-py
* - Uses requests-oauthlib with xauth.
* - However, this seems quite poorly implemented: creates a new OAuth1 object for every request.
    (and does not use any session stuff, only requests.post() and requests_oauthlib.OAuth1)
    But does show how to do xAuth with requests_oauthlib.OAuth1, just do:
        requests_oauthlib.OAuth1(self.consumer_key, self.consumer_secret,
                                 self.user_key, self.user_secret)
        where user_key is username and user_secret is user password.
    This, again, is just the same args to oauthlib.oauth1.Client.
    Not sure if the xAuth workflow is the same as Instapaper/Twitter ??



More OAuth refs:
* github.com/Mashape/mashape-oauth/blob/master/FLOWS.md#oauth-10a-xauth ("The OAuth Bible")


oauthlib details:
* oauthlib/oauth1/rfc5849/parameters.py:prepare_headers() - is in charge of setting the Authorization: header


"""

#import oauthlib
from requests_oauthlib import OAuth1Session #, OAuth1




class XAuthSession(OAuth1Session):
    """
    Requests session with xAuth style OAuth authorization.
    """


    def request_access_tokens(self, url, username, password='', mode='client_auth'):
        """
        OAuth1 authentification using xAuth workflow.
        This is basically rather simple:
        1) Username and password is sent to the server using a POST
           request. While OAuth parameters in the Authorization: header (not in the query string or body).
           But, these xauth parameters are passed as a urlencoded line
           in the request-body. (Similar to the returned tokens)
           The parameters are:
                x_auth_username: The user's username.
                x_auth_password: The user's password, if the account has one.
                x_auth_mode: Must be the value "client_auth".
        2) Server returns oauth_token and oauth_token_secret in qline format (qsl),
                oauth_token=aabbccdd&oauth_token_secret=efgh1234
           These are also known as OAuth access_token and secret.
           In the oauthlib jargon, oauth_token and -_secret is also known as
           resource_owner_key and resource_owner_secret.
        3) The response is parsed with urllib.parse.parse_qsl, and the dict
           is used to update the this session's auth client via ._populate_attributes(tokens)
        """
        p = {'x_auth_username': username,
             'x_auth_password': password,
             'x_auth_mode': mode}
        # params are URL parameters, appended to the URL.
        # If data is a dict, then request will perform form-encoding.
        r = self.post(url, data=p)
        # parse_qsl is also used by oauthlib's urldecode.
        tokens = urllib.parse.parse_qsl(r.text)
        self._populate_attributes(tokens)



