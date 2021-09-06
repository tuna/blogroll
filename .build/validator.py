#!/usr/bin/env python2

from os import sys,path,environ

environ['LANGUAGE'] = 'en'

import urllib2
# OK I know I cannot write python
sys.path.append(path.join(path.dirname(__file__), 'feedvalidator', 'src'))

from bs4 import BeautifulSoup
import feedvalidator

with open(sys.argv[1], 'r') as opmlFile:

    opml = opmlFile.read().decode('utf-8')
    opml = BeautifulSoup(opml, 'xml')

    entries = opml.find_all('outline')

    total = len(entries)

    # Ones that failed the connectivity test
    siteFailed = []

    # Ones that failed the feed validator test
    feedCritical = []

    # Ones that triggered feed validator warnings
    feedWarning = []

    for entry in entries:
        title = entry.get('title').encode('utf-8')
        print '=== Validating %s ===' % title

        site = entry.get('htmlUrl')
        code = -1
        print "Testing HTTP connectivity...: %s" % site 
        try:
            resp = urllib2.urlopen(site)
            code = resp.getcode()
        except Exception as e:
            print "Cannot connect to site: %s" % str(e)
            siteFailed.append([title, entry])

        if code >= 200 and code < 400:
            # Is a valid response
            print "Site successfully responded with code %s" % code
        elif code >= 0:
            print "Site responded with unexpected response code %s" % code
            siteFailed.append([title, entry])

        print "Fetching feeds..."
        feed = entry.get('xmlUrl')

        events = None
        try:
            events = feedvalidator.validateURL(feed, firstOccurrenceOnly=1)['loggedEvents']
        except feedvalidator.logging.ValidationFailure as vf:
            events = [vf.event]
        except Exception as e:
            print "Unable to fetch feed: %s" % str(e)
            feedCritical.append(e)

        if events is not None:
            from feedvalidator import compatibility
            from feedvalidator.formatter.text_plain import Formatter

            criticals = compatibility.A(events)
            if len(criticals) > 0:
                print "Feed failed validation with critical errors:"
                output = Formatter(criticals)
                print "\n".join(output)
                feedCritical.append([title, entry])
            else:
                warnings = compatibility.AAA(events)
                if len(warnings) > 0:
                    print "Feed passed validation with warnings:"
                    output = Formatter(warnings)
                    print "\n".join(output)
                    feedWarning.append([title, entry])
                else:
                    print "Feed passed validation with no error or warning"

        print ""

    print "### SUMMARY ###"
    print "In total of %s entries:" % len(entries)
    print "%s entries failed the connectivity test:" % len(siteFailed)
    for [title, entry] in siteFailed:
        print "\t%s: %s" % (title, entry)
    print ""

    print "%s entries failed the feed validation:" % len(feedCritical)
    for [title, entry] in feedCritical:
        print "\t%s: %s" % (title, entry)
    print ""

    print "%s entries passed the feed validation with warnings:" % len(feedWarning)
    for [title, entry] in feedWarning:
        print "\t%s: %s" % (title, entry)
    print ""

    if len(feedCritical) > 0:
        sys.exit(1)
