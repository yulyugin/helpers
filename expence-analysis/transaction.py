"""
    transaction.py - internal representation for transaction.

    Copyright (C) 2017 Evgeny Yulyugin

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import re

categories = {}
patterns = []

def read_categories(filename):
    def add_pattern(ret, name, category, pattern_str):
        pattern = {}
        pattern['reobj'] = re.compile(pattern_str)
        pattern['name'] = name

        if name in ret.keys():
            if ret[name] != category:
                raise Exception("Name %s matches multiple categories: %s" +
                                    " and %s in file %s"
                                    % (name, ret[name], categories, filename))
            return

        patterns.append(pattern)
        ret[name] = category

    f = open(filename, 'r')
    ret = {}
    category = u""
    for line in f.readlines():
        line = line.split('#', 1)[0] # remove comments
        line = line.strip()
        if line == '':
            continue

        if line.startswith('[') and line.endswith(']'):
            category = line[1: -1]
            continue

        if "*" in line:
            name = line.replace("*", "")
            add_pattern(ret, name, category, line.replace("*", ".*") + "$")

        if "[" in line and "]" in line:
            # TODO: error checks
            name = line.split("[")[0]
            add_pattern(ret, name, category, line.replace("]", "]+") + "$")

        if line in ret.keys():
            raise Exception("Duplicated recipient %s in %s" % (line, filename))

        ret[line] = category
    return ret

def get_category(recipient):
    global categories
    if not categories:
        categories = read_categories("categories.txt")

    if recipient.isdigit():
        return "Account"

    ret = "Unknown"
    try:
        ret = categories[recipient]
    except KeyError:
        for p in patterns:
            if p['reobj'].match(recipient):
                return categories[p['name']]

        print("Unknow category: %s" % recipient)
    return ret

def str2number(num_str):
    return float(num_str.replace(',', ''))

class Transaction:
    def __init__(self, date, recipient, amount):
        self.date = date

        if type(amount) == str:
            amount = str2number(amount)
        self.amount = abs(amount)
        self.is_expense = amount < 0

        self.recipient = recipient
        if self.is_expense:
            self.category = get_category(recipient)
        else:
            self.category = "Refill"
