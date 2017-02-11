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

from datetime import datetime, date
import re

import categories

def str2date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

def str2number(num_str):
    return float(num_str.replace(',', ''))

class Transaction:
    def __init__(self, date, recipient, amount):
        self.date = str2date(date)

        recipient = recipient.strip()
        self.resipient = recipient
        self.category = categories.get_category(recipient)

        amount = str2number(amount)
        self.amount = abs(amount)
        self.is_expense = amount < 0
