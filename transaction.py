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

categories = {}

def read_categories(filename):
    f = open(filename, 'r')
    ret = {}
    category = ""
    for line in f.readlines():
        line = line.strip()
        if line == '':
            continue

        if line.startswith('[') and line.endswith(']'):
            category = line[1: -1]
            continue

        if line in ret.keys():
            raise Exception("Duplicated recipient in %s" % filename)

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
        print "Unknow category: %s" % recipient
    return ret

def str2number(num_str):
    return float(num_str.replace(',', ''))

class Transaction:
    def __init__(self, date, recipient, amount):
        self.date = date

        self.resipient = recipient
        self.category = get_category(recipient)

        amount = str2number(amount)
        self.amount = abs(amount)
        self.is_expense = amount < 0
