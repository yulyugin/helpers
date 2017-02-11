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
        labels.append('{0} - {1:.1f}%'.format(i[1], 100. * i[0] / total))

    pie = plt.pie(payments, startangle=90)
    plt.axis('equal')
    plt.tight_layout()
    legend = plt.legend(pie[0], labels, loc='upper left', fontsize=10)

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
