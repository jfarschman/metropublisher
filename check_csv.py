#!/usr/bin/python
# -*- coding: utf-8 -*-

""" - checkcsv.py
Check CSV is a simple tool that reads the csv file for any kind of
input errors prior to attempting an import into Metro Publisher via
the API. If you place a simple field (createdate) at the end of the
columns and run `./check_csv.py filename.csv` it should print the 
last column.  If you see anything except the final field, then you 
have some additional formatting cleanup work to complete.
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

checkfile = str(sys.argv[1])

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

csvFile = csv.reader(open(checkfile, "rb"), doublequote='false')
for row in csvFile:

        title       = row[0]
        urlname     = row[1]
        section     = row[2]
        authorid    = row[3]
        tagid       = row[4]
        description = row[5]
        fulltext    = row[6]
        createdate  = row[7]

        print(createdate)
