#!/usr/bin/python
# -*- coding: utf-8 -*-
""" - put_articles.py

`put_articles.py` is used to import a csv file into the Metro Publisher
using their API. The format of that article should be "field1", "field2"
where infield quotes are escaped with doublequotes.

You will need to setup environment variables for variables specific to 
your installation.  For example:

        export APIKEY=YOUR_API_KEY
        export APISECRET=YOUR_API_KEY
        export APIID=YOUR_API_SITE_ID

Additionally, be sure to use the `check_csv.py` to make sure your data if
properly importing prior to running this script.

Syntax:
        ./put_articles.py

"""
__author__ = "Jay Farschman"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Jay Farschman"
__email__ = "jfarschman@gmail.com"
__status__ = "Production"

import sys
import logging 
import time 
import uuid
from pprint import pprint
import csv
import os
import van_api

""" Import the working file """
importfile = str(sys.argv[1])

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

""" Connect to the API """
apikey = os.environ["APIKEY"]
apisecret = os.environ["APISECRET"]
apiid = os.environ["APIID"]

credentials = van_api.ClientCredentialsGrant(apikey, apisecret)
api = van_api.API('api.metropublisher.com', credentials)

""" Generate Unique UUID for the import"""
content_upload_uuid = uuid.uuid1()

csvFile = csv.reader(open(importfile, "rb"), doublequote='false')
for row in csvFile:

        title       = row[0]
        urlname     = row[1]
        section     = row[2]
        authorid    = row[3]
        tagid       = row[4]
        description = row[5]
        fulltext    = row[6]
        createdate  = row[7]

        logging.info("Sending Article - %s" % (title)) 
        logging.info("  --- Submiting with uuid of %s" % (content_upload_uuid))
        result = api.PUT('/%s/content/%s' % (apiid, content_upload_uuid),
                        {"urlname": "%s" % (urlname),
                                "content_type": "article",
                                "created": "%s" % (createdate),
                                "issued": "%s" % (createdate),
                                "title": "%s" % (title),
                                "state": "published",
                                "description": "%s" % (description),
                                "content": "%s" % (fulltext),
                                "section_uuid": "%s" % (section)})
        logging.info("  --- Applying %s to %s " % (tagid, content_upload_uuid))
        time.sleep(1)
        result = api.PUT('/%s/tags/%s/describes/%s' % (apiid, tagid, content_upload_uuid),
                        {"created": "%s" % (createdate)})
        logging.info("  --- Setting %s as author of %s " % (authorid, content_upload_uuid))
        time.sleep(1)
        result = api.PUT('/%s/tags/%s/authored/%s' % (apiid, authorid, content_upload_uuid),
                        {"created": "%s" % (createdate)})
        time.sleep(1)
        logging.info("Completed article - %s" % (title))

logging.info("FINISHED THE ENTIRE RUN")
