"""
    expence_from_csv.py - get expense data from CSV file produces by SEB bank.
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

import csv
from itertools import islice
from transaction import Transaction

def expense_reader(filename):
    """
    File format:
    Accounting date, currency date, verification number, receiver, amount, balance
    """
    ret = list()
    with open(filename, 'rb') as csvfile:
        expense_reader = csv.reader(csvfile)
        for i in islice(expense_reader, 5, None):
            ret.append(Transaction(i[1], i[3], i[4]))
    return ret
