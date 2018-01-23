#!/usr/bin/python3

import re
import sys
import urllib.request
from html.parser import HTMLParser

root_url = "http://old.stockholmslansmuseum.se/faktabanken/visa-runa/"

class RunstenParser(HTMLParser):
    PENDING = 0
    NAME = 1
    PARISH_INFO = 2
    DESCRIPTION = 3
    COMMENT = 4

    def __init__(self):
        super(RunstenParser, self).__init__()
        self.stage = self.PENDING
        self.tag = None
        self.longitude = 0.
        self.latitude = 0.
        self.name = ""

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.tag = tag
        elif tag == "h2":
            self.tag = tag
            self.stage = self.NAME
        elif tag == "p" and self.stage != self.PENDING:
            self.stage += 1
        else:
            pass

    def handle_endtag(self, tag):
        if tag == self.tag:
            self.tag = None

    def handle_data(self, data):
        if self.tag == "script":
            # Extracting coordinates
            m = re.search("GLatLng\(([0-9]*\.[0-9]*), ([0-9]*\.[0-9]*)\)", data)
            if m:
                self.latitude = m.groups(0)[0]
                self.longitude = m.groups(0)[1]

            # Extracting name
            m = re.search("var name = \"(.*)\";", data)
            if m:
                self.name = m.groups(0)[0]
        elif self.tag == "h2":
            assert self.name == data

        if self.stage == self.COMMENT:
            print(data)
            self.stage = self.PENDING

def main():
    i = 4
    while True:
        runsten_url = root_url + str(i)
        data = urllib.request.urlopen(runsten_url).read()

        runsten_data = RunstenParser()
        runsten_data.feed(data.decode('utf-8'))
        i += 1
        break
    return 0

if __name__ == "__main__":
    sys.exit(main())
