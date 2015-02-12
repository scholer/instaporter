# instaporter
Do you have access to access-protected content? Want to read add it to your Instapaper reading list?
Instaporter allows you to retrieve protected content and then upload it to your Instapaper reading list.

This application allows you to upload locally-available resources to
Instapaper using the Instapapers API (requires a premium account).

The application has several modes of operation, all involving interaction
with Instapaper through the REST API.

One mode of operation will retrieve access-protected content from a URL
and upload it to your Instapaper reading list. This is similar to the
Instapaper chrome extension, but does not require chrome to operate.
This is particularly useful if you have access to content which is
not publicly available, e.g. articles from scientific journals.
These are often only available from within your university's IP range,
and thus not readable by Instapaper's parsing server.

Another mode of operation can be used to upload html content from local files.

The application includes a python module to consume the Instapaper API
via the requests library and the requests-oauthlib extension.
Requests is more powerful and easier to use than the httplib2 library
used by python-oauth2, which is what other python Instapaper libraries
currently use.

If Instaporter proves useful, the goal is to port the code to Android
(where chrome extensions are not currently available).

The application does not allow you to "automatically" upload arbitrary
content from websites as it is being published. This would violate Instapaper's
Terms of Usage, which requires the user to take confirmative (per-item)
action, e.g. "star" an article, click a button, or similar.


Note: The name "Instaporter" is a contraction of "Instapaper" and "Transporter".
