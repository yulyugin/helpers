"""
    analyse.py - perform expense analysis.

    Copyright (C) 2017 Evgenii Iuliugin

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

import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta, datetime, date
from enum import Enum
from calendar import monthrange
from copy import deepcopy

class Granularity(Enum):
    Week = 0
    Month = 1
    Year = 2

def total_expense(transactions, skip_account_transfers = True):
    total = 0.
    for t in transactions:
        if skip_account_transfers and t.category == 'Account':
            continue
        if t.is_expense:
            total += t.amount
    return total

def pie_chart(groups, total = 1.):
    payments = []
    labels = []
    g_sorted = sorted(((v,k) for k,v in groups.items()), reverse=True)
    for i in g_sorted:
        payments.append(i[0])
        labels.append('{} - {:,.2f} ({:.1f}%)'.format(i[1], i[0], 100. * i[0] / total))

    # Draw a pie chart
    pie = plt.pie(payments, startangle=90)
    plt.axis('equal')
    plt.tight_layout()

    # Create a blank rectangle to add total label
    extra = plt.Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
    pie[0].append(extra)
    labels.append("Total - {:,.2f}".format(total))

    # Add a legend
    legend = plt.legend(pie[0], labels, loc='upper left', fontsize=10)

    plt.show()

def histogram(data, categories, labels, period_name):
    index = np.arange(len(labels))
    b = [0] * len(labels)
    i = 0
    for d in data:
        plt.bar(index, d, bottom=b)
        b = [b[i] + d[i] for i in range(len(b))]
        i+=1
    plt.xticks(index, labels, rotation=45, horizontalalignment='right')
    plt.grid(axis='y', linestyle='--')
    plt.legend(categories, loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()

def category_analysis(transactions, skip_account_transfers = True):
    categories = {}
    total = 0.
    for t in transactions:
        if skip_account_transfers and t.category == 'Account':
            continue
        if not t.is_expense:
            continue
        try:
            categories[t.category] += t.amount
        except KeyError:
            categories[t.category] = t.amount
        total += t.amount

    pie_chart(categories, total)

class AnalysisResult():
    def __init__(self):
        # amount[category] = [amount0, amount1, ...]
        # amount[category][i] - amount spent for category during period i
        # periods[i] - name of period i
        self.amount = {}
        self.total = []
        self.periods = []

    def new_category(self, category):
        if len(self.periods) <= 1:
            self.amount[category] = []
            self.amount[category].append(0)
        else:
            self.amount[category] = []
            for i in range(len(self.periods)):
                self.amount[category].append(0)

    def add_expense(self, category, amount):
        try:
            self.total[-1] += amount
        except:
            self.total.append(0)

        try:
            self.amount[category][-1] += amount
        except KeyError:
            self.new_category(category)
            self.amount[category][-1] += amount

    def add_period(self, description):
        self.periods.append(description)
        for c in self.amount.values():
            c.append(0)

    def optimize_categories(self):
        for category in list(self.amount.keys()):
            active_periods = 0.
            total_periods = 0.
            for period in self.amount[category]:
                total_periods += 1
                if period != 0:
                    active_periods += 1

            if total_periods / active_periods > 4:
                for i in range(int(total_periods)):
                    try:
                        self.amount['Other'][i] += self.amount[category][i]
                    except KeyError:
                        self.new_category('Other')
                        self.amount['Other'][i] += self.amount[category][i]
                del self.amount[category]

def get_last_date(the_date, granularity):
    if granularity == Granularity.Week:
        # Closest Sunday
        return the_date + timedelta((13 - the_date.weekday()) % 7)
    if granularity == Granularity.Month:
        return date(the_date.year, the_date.month,
                    monthrange(the_date.year, the_date.month)[1])

def get_name(granularity):
    if granularity == Granularity.Week:
        return "week"
    if granularity == Granularity.Month:
        return "month"

def comparative_analysis(transactions, skip_account_transfers = True,
                         granularity = Granularity.Month):
    last_date = datetime.min.date()
    result = AnalysisResult()
    for t in transactions:
        if skip_account_transfers and t.category == 'Account':
            continue
        if not t.is_expense:
            continue

        if t.date <= last_date:
            # Current period. Update the result
            result.add_expense(t.category, t.amount)
        else:
            # Next period
            first_date = t.date
            last_date = get_last_date(t.date, granularity)
            result.add_period("{0:%b %d} - {1:%b %d}".format(first_date,
                                                             last_date))
            result.add_expense(t.category, t.amount)
    result.optimize_categories()
    histogram(result.amount.values(), result.amount.keys(), result.periods,
              get_name(granularity))

def optimize(transactions, skip_account_transfers = True):
    """
    If expense per category is less than 1% than category name is changes to
    'Other' for all transactions that maches this category.
    """
    categories = {}
    total = 0.
    for t in transactions:
        if skip_account_transfers and t.category == 'Account':
            continue
        if not t.is_expense:
            continue
        try:
            categories[t.category] += t.amount
        except KeyError:
            categories[t.category] = t.amount
        total += t.amount

    for t in transactions:
        if skip_account_transfers and t.category == 'Account':
            continue
        if not t.is_expense:
            continue
        if categories[t.category] < (total * 0.01):
            t.category = 'Other'
