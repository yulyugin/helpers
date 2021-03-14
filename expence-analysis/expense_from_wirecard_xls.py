"""
    expence_from_wirecard_xls.py - get expense data from XSL file produced by
    wirecard bank.
    Copyright (C) 2021 Evgenii Iuliugin

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

import xlrd
from datetime import datetime
from itertools import islice

from transaction import Transaction

def expense_reader(filename):
    ret = []

    rows_to_skip = 1
    amount_column = 1
    date_column = 10
    receiver_column = 18

    book = xlrd.open_workbook(filename)
    sheet = book.sheet_by_index(0)
    for rx in range(rows_to_skip, sheet.nrows):
        row = sheet.row(rx)
        amount = row[amount_column].value
        if amount  == '0.00':
            continue
        date = datetime.strptime(row[date_column].value, "%d/%m/%Y").date()
        ret.append(Transaction(date, row[receiver_column].value, amount))

    return ret
