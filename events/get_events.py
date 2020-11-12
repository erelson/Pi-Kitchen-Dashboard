#! /usr/bin/env python

# Copyright (c) 2018 Eric Relson
# Author: Eric Relson

import calendar
import datetime
import os

import eventful

# Either grab from $EVENTFUL_KEY in the environment, or put the API key directly in script here
API_KEY = os.getenv("EVENTFUL_KEY", "OR_PUT_KEY_HERE")

# You can find the Venue ID by searching at eventful.com for an event at the venue,
# then clicking the venue name and taking the tail end of the URL, e.g.:
# http://eventful.com/annarbor/venues/michigan-stadium-/V0-001-000106763-0
LOCATION_ID = 'V0-001-011627287-1'

try:
    api = eventful.API(API_KEY)

    # support of multiple venues is easy if you want...
    venue_list = [LOCATION_ID,
                  # Other IDs...,
                 ]
    events = []
    pagesize = 10
    for venue_id in venue_list:
        
        vdata = api.call('events/search', location=venue_id, page_size=pagesize, sort_order="date")
        #if vdata['total_items'] > pagesize:
        #    for pg in range(2,
        #                    vdata['total_items'] / pagesize +
        #                    int(bool(vdata['total_items'] % pagesize)) + 1):
        #        vdata = api.call('events/search', location=venue_id, page_size=pagesize, page=pg, sort_order="date")
        events.extend(vdata['events']['event'])

    ## Simple display of everything
    #with open("events.txt", 'w') as fw:
    #    for ev in events:
    #        day = calendar.day_name[
    #                datetime.datetime(*(map(int, ev["start_time"][:10].split('-')))).weekday()
    #        ]
    #        fw.write('<b>' + day + " " + ev["start_time"][5:-3] + '</b>\n'
    #                '<br>' + ev["title"] + "\n<br>")
    #                #'<br><marquee behaviour="alternate">' + ev["title"] + "</marquee>\n<br>")

    # Group events by day, keep earliest time.
    # I do this because in my case I care about when traffic will be bad
    # around a football stadium and/or parking will be scarce.
    prevdate = None
    line_cnt = 0
    with open("events.html", 'w') as fw:
        for ev in events:
            date = ev["start_time"][:10]
            if date != prevdate:
                if prevdate is not None:
                    fw.write('<br>') # gap between days' events
                    line_cnt += 1
                day = calendar.day_name[
                        datetime.datetime(*(map(int, date.split('-')))).weekday()
                ]
                fw.write('<b>' + day + " " + ev["start_time"][5:-3] + '</b>\n<br>')
                prevdate = date
                line_cnt += 1
            fw.write(ev["title"] + "\n<br>")
            line_cnt += 1

            # Limit to 20 lines of date/event info
            if line_cnt + 3 > 20:
                break

    print("Created events.html!")

    with open("get_events.log", 'a') as fw:
        fw.write(datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S") +
                " Grabbed events and wrote to events.html\n")

except Exception as e:
    with open("get_events.log", 'a') as fw:
        fw.write(datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S") + " FAILURE: " + str(e) + "\n")
