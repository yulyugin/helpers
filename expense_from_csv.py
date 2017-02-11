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
from datetime import datetime, date
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

        # Skip lines that doesn't contatin relevant transaction information
        for i in islice(expense_reader, 5, None):
            # Remove trailing spaces
            receiver = i[3].strip()
            date = None

            # Receiver are usually in "Name/YY-MM-DD" format.
            # Separate these fields
            namedate = receiver.split('/')
            if len(namedate) == 2:
                date = datetime.strptime(namedate[1], "%y-%m-%d")
                receiver = namedate[0].strip()
            else:
                # Use currency date if date is not available in receiver field
                date = datetime.strptime(i[1], "%Y-%m-%d")

            ret.append(Transaction(date, receiver, i[4]))

    return ret
