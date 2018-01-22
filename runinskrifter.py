#!/usr/bin/python3

from enum import Enum
import sys
import urllib.request
from html.parser import HTMLParser

root_url = 'https://www.runinskrifter.net/signum'
lands = ['U', 'Sö']

class Runsten():
    def __init__(self, name):
        self.name = name
        self.alive = True
        self.longitude = 0.
        self.latitude = 0.

    def __repr__(self):
        coordinates = ''
        if self.latitude != 0 and self.longitude != 0:
            coordinates = ' ({}, {})'.format(self.latitude, self.longitude)
        return "%s%s%s" % (self.name, "" if self.alive else "†", coordinates)

class RootHTMLParser(HTMLParser):
    def __init__(self):
        super(RootHTMLParser, self).__init__()
        self.active = False
        self.runstenar = list() # [(name, alive?), ...]

    def handle_starttag(self, tag, attrs):
        if tag == 'li':
            self.active = True

    def handle_endtag(self, tag):
        if tag == 'li':
            self.active = False

    def handle_data(self, data):
        if self.active:
            if "†" not in data: # dead mark
                self.runstenar.append(Runsten(data))
            else:
                self.runstenar[-1].alive = False

class RunstenParser(HTMLParser):
    PENDING = 0
    LATITUDE = 1
    LONGITUDE = 2

    def __init__(self):
        super(RunstenParser, self).__init__()
        self.stage = 0 # pending
        self.active = False
        self.longitude = 0.
        self.latitude = 0.

    def handle_starttag(self, tag, attrs):
        if tag == 'data':
            self.stage += 1
            self.active = True

    def handle_endtag(self, tag):
        if tag == 'data':
            self.active = False

    def handle_data(self, data):
        # (degrees, minutes, seconds) to degrees
        def dms2d(dms):
            d = float(dms.split("°")[0])
            m = float(dms.split("′")[0].split('°')[1])
            s = float(dms.split("′")[1][0:-1])
            degrees = d + (m + s / 60) / 60
            return degrees

        if self.active:
            if self.stage == self.LATITUDE:
                self.latitude = dms2d(data)
            elif self.stage == self.LONGITUDE:
                self.longitude = dms2d(data)

def main():
    runstenar = list()
    for land in lands:
        land_url = root_url + '/' + land
        land_url = urllib.parse.quote_plus(land_url, ':/')
        data = urllib.request.urlopen(land_url).read()

        parser = RootHTMLParser()
        parser.feed(data.decode('utf-8'))
        for runsten in parser.runstenar:
            runsten_url = root_url + '/' + land + '/' + runsten.name.split()[1]
            runsten_url = urllib.parse.quote(runsten_url, ':/')
            data = urllib.request.urlopen(runsten_url).read()

            runsten_data = RunstenParser()
            runsten_data.feed(data.decode('utf-8'))
            runsten.latitude = runsten_data.latitude
            runsten.longitude = runsten_data.longitude
        runstenar.extend(parser.runstenar)

    flive = open('live.txt', 'w')
    fdead = open('dead.txt', 'w')
    template = "type=\"waypoint\" latitude=\"%f\" longitude=\"%f\" name=\"%s\"\n"
    for runsten in runstenar:
        if runsten.alive:
            flive.write(template % (runsten.latitude, runsten.longitude, runsten.name))
        else:
            fdead.write(template % (runsten.latitude, runsten.longitude, runsten.name))

    return 0

if __name__ == "__main__":
    sys.exit(main())
