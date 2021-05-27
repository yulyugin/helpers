#!/usr/bin/env python3

import urllib.request
import ssl
from html.parser import HTMLParser
import time
import copy
import argparse
import threading

class Item():
    def __init__(self):
        self.url = None
        self.title = None

    def to_string(self):
        return f'{self.title} ({self.url})'

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()

    def __eq__(self, other):
        if self.url == other.url and self.title == other.title:
            return True
        return False

class VendHTMLParser(HTMLParser):
    def __init__(self):
        super(VendHTMLParser, self).__init__()
        self.items = []

        self.in_item = False
        self.in_header = False

        self.url_base = 'https://vend.se'

    def handle_starttag(self, tag, attrs):
        if tag == 'article':
            assert not self.in_item, 'Nested items?'
            self.in_item = True
            self.items.append(Item())
            return
        if self.in_item:
            if tag == 'h4':
                self.in_header = True
                return
        if self.in_header:
            if tag == 'a':
                self.items[-1].url = self.url_base + attrs[0][1]

    def handle_endtag(self, tag):
        if tag == 'article':
            assert self.in_item, 'Nested items?'
            self.in_item = False
            self.url = None
            self.title = None
        if self.in_item and tag == 'h4':
            assert self.in_header, 'Nested header?'
            self.in_header = False

    def handle_data(self, data):
        if self.in_item:
            if self.items[-1].url and not self.items[-1].title:
                self.items[-1].title = data

class UrlMonitor(threading.Thread):
    def __init__(self, url, interval):
        super().__init__()
        self.url = url
        self.interval = interval
        self.daemon = True

    def run(self):
        self.monitor_url()

    def get_list(self):
        data = urllib.request.urlopen(
            self.url, context=ssl._create_unverified_context()).read()
        parser = VendHTMLParser()
        parser.feed(data.decode('utf-8'))
        return parser.items

    def monitor_url(self):
        def get_new_items(new, current):
            new = copy.deepcopy(new)
            for c in current:
                try:
                    new.remove(c)
                except ValueError:
                    # It's okay for items to disappear from the new list
                    pass
            return new

        print(f'Starting to check "{self.url}" every'
              f' {self.interval/60} minutes.')

        current = self.get_list()
        while True:
            time.sleep(self.interval)
            new = self.get_list()
            new_items = get_new_items(new, current)
            if new_items:
                print(new_items)
            current = new

def main():
    parser = argparse.ArgumentParser(
        description='Monitor specified URLs for new items to appear.')
    parser.add_argument('-i', '--interval', nargs='?', type=int, action='store',
                        default=5 * 60, help='interval specifying how'
                        ' often provided URLs should be checked')
    parser.add_argument('-u', '--url', required=True, nargs='?', type=str,
                        action='store', help='URL to monitor')
    args = parser.parse_args()
    thread = UrlMonitor(args.url, args.interval)
    thread.start()
    thread.join()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted by user')
