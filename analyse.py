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
from datetime import timedelta, datetime
from enum import Enum

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

def histogram(data, labels):
    width = 1
    space = 2 * width
    shift = width * len(data[0]) + space
    ind = np.arange(len(data[0]))

    # Create a color map
    norm = plt.Normalize()
    colors = plt.cm.jet(norm(data[-1]))

    for i in xrange(len(data)):
        plt.bar(ind + shift * i, data[i], width, color = colors)

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
        # amount[category] = [amount0, amount1, ...] list of amount for each period
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

def get_last_date(the_date, granularity):
    if granularity == Granularity.Week:
        # Closest Sunday
        return the_date + timedelta((13 - the_date.weekday()) % 7)

def comparative_analysis(transactions, skip_account_transfers = True,
                         granularity = Granularity.Week):
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
            last_date = get_last_date(t.date, granularity)
            result.add_period("period") # TODO
            result.add_expense(t.category, t.amount)
    histogram(result.amount.values(), result.periods)
