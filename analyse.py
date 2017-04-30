"""
    analyse.py - module that is doing expense analysis.

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

import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta, datetime, date
from enum import Enum
from calendar import monthrange

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
    g_sorted = sorted(((v,k) for k,v in groups.iteritems()), reverse=True)
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
    width = 1
    space = 2 * width
    shift = width * len(data[0]) + space
    ind = np.arange(len(data[0]))

    # Create a color map
    norm = plt.Normalize()
    colors = plt.cm.jet(norm(data[-1]))

    fig = plt.figure()
    ax = fig.add_subplot(111)

    label_colors = list()
    for i in xrange(len(data)):
        label_colors = ax.bar(ind + shift * i, data[i], width, color = colors)

    # Axes and labels
    ax.set_title("Expenses by categories and {}".format(period_name))
    xind = np.arange(len(data))
    for i in xind:
        # Aligned to the center of data
        xind[i] = (shift - space) / 2 + shift * i
    ax.set_xticks(xind)
    xticks = ax.set_xticklabels(categories)
    plt.setp(xticks, rotation=45, fontsize=10)

    plt.legend(label_colors, labels, loc='upper left', fontsize=10)
    plt.grid(axis = 'y')

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
        self.amount['Total'] = []
        self.periods = []

    def new_category(self, category):
        if len(self.periods) <= 1:
            self.amount[category] = []
            self.amount[category].append(0)
        else:
            self.amount[category] = []
            for i in xrange(len(self.periods)):
                self.amount[category].append(0)

    def add_expense(self, category, amount):
        self.amount['Total'][-1] += amount
        try:
            self.amount[category][-1] += amount
        except KeyError:
            self.new_category(category)
            self.amount[category][-1] += amount

    def add_period(self, description):
        self.periods.append(description)
        for c in self.amount.values():
            c.append(0)

    def filter_rare_categories(self, min_number=3):
        for category in self.amount.keys():
            active_periods = 0
            for period in self.amount[category]:
                if period != 0:
                    active_periods += 1

            if active_periods < min_number:
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
    result.filter_rare_categories()
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
