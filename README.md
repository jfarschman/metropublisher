# metropublisher

#### Table of Contents

1. [Overview](#overview)
2. [In a Nutshell](#Nutshell)
3. [Usage - How to Start](#usage)
    * [Install API Client](#install-api-tools)
    * [Exporting Data](#exporting-data)
    * [Checking Data](#checking-data)
    * [Importing Data](#importing-data)
4. [Limitations - OS compatibility, etc.](#limitations)
5. [Contributors](#contributors)

## Overview
Tools for interacting with Metro Publisher's API.

## Nutshell
This project is a walkthrough of pulling data out of a Joomla MySQL DB
and formatting it for inpupt into Metropublisher using their API. This
is a data migrtation and as such the bulk of the work will be in setting
up properly formated CSV files which you may check with `check_csv.py`
and then the import is accomplished with `put_articles.py`.

## Usage

### Install API Tools
The API client library tools are supplied by Vanguardistas and are
available here https://github.com/vanguardistas/van_api

```bash
git clone https://github.com/vanguardistas/van_api.git
./setup.py
```
To test, there are some example scripts and I believe `get_sections.py`
will allow out to against the demo site. Of course, you will need to 
generate your own API key and secret before you interact with your own
site.

### Exporting Data
I spent the majority of my time on this step which is basically mapping
data from one CMS into another.  For this I simple did a mysqldump of 
all of my data and spun it up on another MySQL server where I worked.

NOTE BENE: Work with caution and do not work on your live website with
these or any other SQL commands that you don't understand. At each step
of the way check and double check your data.

I have cleaned up my commands and not included them all here, because
every installation is different and for users of the CMS I worked on 
did not use it exactly as intended.

#### JOOMLA (1.x)
First a brief survey to discover the categories, sections and authors.
You need to build a datamap where you decide which fields will move and
where they will go. So, first discover what you have.
```bash
# Finds the individual IDs, but no cont
SELECT DISTINCT(`Catid`) FROM `_content`

# Count Categories
SELECT `catid`,COUNT(*) as count FROM `_content` GROUP BY `catid` ORDER BY `catid` ASC

# Count Sections
SELECT `sectionid`,COUNT(*) as count FROM `_content` GROUP BY `sectionid` ORDER BY `sectionid` ASC

# Count by Author - Mostly Wrong
SELECT `created_by`,COUNT(*) as count FROM `_content` GROUP BY `created_by` ORDER BY `created_by` ASC

# Extract Authors from introtext
SELECT *  FROM `_content` WHERE `introtext` LIKE '%%>by %%'

# Responsive websites don't allow embedded <img {attribute} tags 
# I wanted a count to see how much work it would be to move these 
# manually
SELECT `title`, `_content.urlname`, `fulltext`, DATE_FORMAT(`created`, '%Y-%m-%dT%TZ') as date FROM `_content` WHERE `fulltext` LIKE '%%<img %%'
```
RULE #1 - If you don't need it don't import it.
Do some data clean-up.  If you site is like the one I worked on there
will be lots of unused, or little used categories and sections. These
can be cleaned with commands like:
```bash
# DELETE Lame Records by category
DELETE FROM `_content` WHERE `catid` = 16 OR `catid` = 17 OR 
`catid` = 50 OR `catid` = 51 OR `catid` = 52 OR `catid` = 53 OR
`catid` = 54 OR `catid` = 55 OR `catid` = 56 OR `catid` = 57 OR
`catid` = 58 OR `catid` = 59 OR `catid` = 60 OR `catid` = 62 OR
`catid` = 80 OR `catid` = 82 OR `catid` = 102 OR `catid` = 105
```

RULE #2 - No hard returns, <br /> or &nbsp in your article field.
```
UPDATE _content SET _content.fulltext = REPLACE(_content.fulltext,'\r\n',' ');
UPDATE _content SET _content.fulltext = REPLACE(_content.fulltext,'<br />',' ');
UPDATE _content SET _content.fulltext = REPLACE(_content.fulltext,'&nbsp;',' ');
```
RULE #3 - If a field doesn't exist, then make it.
In my case I wanted to populate the urlname in Metro Publisher with
the title, but lowercase and with dashes in between.
```
ALTER TABLE `_content` ADD `urlname` VARCHAR(100);
UPDATE `_content` SET `_content.urlname` = LOWER(title);
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`, ' - ', '-' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`, ' ', '-' );
```
RULE #4 - Remove RFC 3986 reserved characters ! * ' ( ) ; : @ & = + $ , / ? # [ ]
These don't belong in an URL.
```
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\!', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\'', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\*', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\(', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\)', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\;', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\:', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\@', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\&', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\=', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\+', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\$', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\,', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\/', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\?', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\#', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\[', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\]', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\|', '' );
UPDATE _content SET `_content.urlname` = REPLACE( `_content.urlname`,'\’', '' );
```
RULE #5 - Map your sections, tags and articles from Joomla categories
I know that every article in category '2' is written by the same author
and belongs in the same section, tagged the same way.
```
UPDATE _content 
SET section_uuid = 'yoursectionuuid', 
    tagid = 'yourtagid',
    authorid = 'yourauthorid'
WHERE `catid` = '2'
```
RULE #6 - Metro Publisher needs an introdoctory sentence.
I got this from a really long introtext in Joomla with this query
```
UPDATE _content SET description = (SELECT SUBSTRING_INDEX( `fulltext` , '.', 1 ))
```
RULE #7 - Test on a subset of your data.
For me category '2' was only 80 articles. The SELECT statement has the fields
we need.  NB: time is formatted for Metro Publisher.
```
SELECT `title`, `urlname`, `section_uuid`, `authorid`, `tagid`, `description`, `fulltext`, DATE_FORMAT(`created`, '%Y-%m-%dT%TZ') as date  FROM `_content` WHERE `catid` = '2'
```
RULE #8 - Export as a CSV with \" escaped quotes.
This is the default for PhyMyAdmin when you select CSV export.

RULE #9 - Work `sed` magic
Some formatting needs to be done in the streams editor rather than SQL
Here we are removing illegal HTML tags from the exported csv.
```
WORK SOME SED MAGIC
sed -i '' 's/<img[^>]*>//g' exported.csv
sed -i '' 's/<span[^>]*>//g' exported.csv
sed -i '' 's/<\/span[^>]*>//g' exported.csv
sed -i '' 's/<div[^>]*>//g' exported.csv
sed -i '' 's/<font[^>]*>//g' exported.csv
sed -i '' 's/<\/font[^>]*>//g' exported.csv
sed -i '' 's/<font[^>]*>//g' exported.csv
sed -i '' 's/<p class[^>]*>/<p>/g' exported.csv
sed -i '' 's/<p align[^>]*>/<p>/g' exported.csv
sed -i '' 's/<o:p[^>]*>/<p>/g' exported.csv
sed -i '' 's/<\/o:p[^>]*>/<p>/g' exported.csv
sed -i '' 's/<p><p[^>]*>/<p>/g' exported.csv

# Python's csvreader cannot break the fields out properly with \" but does
# does well with "" and doublequote=false
sed -i '' 's/\\"/\"\"/g'  exported.csv
```
RULE #10 - You can never be to picky, or can you?
Here I noticed that urlname had some funky --- -- and other problems
that would work, but look lame.  fix, inspect and fix again.
```
# Visually inspect the urlname and clean it up. 
sed -i '' 's/-\.\.\.-/-/g'  exported.csv
sed -i '' 's/-…-/-/g'  exported.csv
sed -i '' 's/-–-/-/g'  exported.csv
sed -i '' 's/--/-/g'  exported.csv
sed -i '' 's/-\.\.\.//g' exported.csv
```
At every step above... after every command inspect your data and make
sure you haven't mangled it. 

### Checking Data
Now you should have a file `exported.csv` that is ready for a text.
Use `check_csv.py` for this test. You will find that the most problematic
fields are those with HTML tags and the least are simple things like
datestamps. For this reason, I setup `createdate` as the final field
and the check should produce.
```
./check_csv.py exported.csv
2009-11-06T00:13:12Z
2009-12-06T15:03:26Z
2010-01-02T23:19:23Z
2010-02-05T13:34:17Z
2010-03-06T16:50:47Z
...
```
If you see something else, then you have some unescaped characters 
that will prevent the import. Open `check_csv.py` and try printing
different fields until you identify the problem field.

If this comes back clean, then you should try importing.

### Importing Data
Limit your import to a single record to start with and then move
up to 5, 50, 500. 

To run this script you will need to setup environment variables 
 specific to your installation.  For example

```
    export APIKEY=YOUR_API_KEY
    export APISECRET=YOUR_API_KEY
    export APIID=YOUR_API_SITE_ID
```
Then pass it your csv file name and the file to catch the exceptions
```
./put_article.py exported.csv invalidrecords.csv
```
This either will interate all of the records and create a file of the 
failed transations called `invalidrecords.csv` for you to clean up and
then try again.  Failures appear to happen in the content field 
```
van_api.APIError: bad_parameters: One or more of your incoming parameters failed validation, see info for details
{u'content': u'Invalid value'
```

## Limitations


## Contributors
Jay Farschman - jfarschman@gmail.com
