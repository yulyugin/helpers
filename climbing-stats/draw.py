#!python3
# Copyright (C) 2022 Evgenii Iuliugin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import json
from collections import OrderedDict
import matplotlib.pyplot as plt
from datetime import date, timedelta

stats_file = "stats.json"

climbing_styles: list[str] = ['Bouldering', 'Top Rope', 'Lead', 'Moonboard']

with open(stats_file, 'r', encoding='utf8') as f:
    stats = json.load(f)

class Climb():
    style: str
    grade: str
    result: str

    def __init__(self, style: str, stats: dict[str, str]):
        self.style = style
        for key, value in stats.items():
            if key != "name":
                self.grade = key
                self.result = value

    def __repr__(self):
        return f'{self.style}({self.grade}, {self.result})'

    def flash(self):
        return self.result == 'flash'

class ClimbingSession():
    place: str
    climb_date: date
    climbs: list[Climb]
    styles: list[str]

    def __init__(self, stats):
        self.climbs = []
        self.styles = []

        for key, value in stats.items():
            if key in climbing_styles:
                self.styles.append(key)
                for c in value:
                    self.climbs.append(Climb(key, c))
            elif key == 'date':
                self.climb_date = date.fromisoformat(value)
            else:
                setattr(self, key, value)

        assert len(self.styles) != 0

    def __repr__(self):
        ret = 'Session('

        if len(self.styles) != 1:
            ret += ', '.join(self.styles[0:-1])
            ret += f' and {self.styles[-1]}'
        else:
            ret += self.styles[0]

        ret += f' at {self.place}'
        ret += f' on {self.date}'
        ret += ')'
        return ret

    def session_stats(self, style):
        ret = []
        for c in self.climbs:
            if c.style == style:
                ret.append(c)
        return ret

sessions: list[ClimbingSession] = []
for s in stats:
    sessions.append(ClimbingSession(s))

def bar_data(sessions: list[ClimbingSession], style: str):
    flash: dict[str, int] = {}
    redpoint: dict[str, int] = {}
    for s in sessions:
        for c in s.session_stats(style):
            if c.grade not in flash:
                flash[c.grade] = 0
                redpoint[c.grade] = 0

            d = flash if c.flash() else redpoint
            d[c.grade] += 1

    flash = OrderedDict(sorted(flash.items()))
    redpoint = OrderedDict(sorted(redpoint.items()))
    return (flash, redpoint)

class CumulativeStats:
    dates: list[date]
    climbs: list[int]

    def __init__(self):
        self.dates = []
        self.climbs = []

    def add_session(self, date: date, total_climbs: int):
        if len(self.climbs) == 0:
            self.climbs.append(total_climbs)
        else:
            self.climbs.append(self.climbs[-1] + total_climbs)
        self.dates.append(date)

def cumulative_data(sessions: list[ClimbingSession], style: str) -> dict[str, CumulativeStats]:
    grades: dict[str, CumulativeStats] = {}
    for s in sorted(sessions, key=lambda x: x.climb_date):
        accums: dict[str, int] = {}
        for c in s.session_stats(style):
            if c.grade not in accums:
                accums[c.grade] = 0
            accums[c.grade] += 1

        for grade, accum in accums.items():
            if grade not in grades:
                grades[grade] = CumulativeStats()
            grades[grade].add_session(s.climb_date, accum)

    return OrderedDict(sorted(grades.items()))

figure, axis = plt.subplots(len(climbing_styles), 2)

for index, style in enumerate(climbing_styles):
    ax = axis[index][0]
    ax.set_title(f'{style} Stats')
    ax.grid(visible=True, axis='y')
    (f, r) = bar_data(sessions, style)
    ax.bar(list(f.keys()), list(f.values()), color='green', label='Flash')
    ax.bar(list(r.keys()), list(r.values()), color='orange', bottom=list(f.values()), label='Redpoint')
    ax.legend()

    ax = axis[index][1]
    ax.set_title(f'Cumulative {style} Stats')
    ax.grid(visible=True, axis='y')
    grades = cumulative_data(sessions, style)
    first_day = last_day = date.today()
    for grade, grade_stats in grades.items():
        first_day = min(first_day, grade_stats.dates[0].replace(day=1))
        last_day = max(last_day,
                (grade_stats.dates[-1].replace(day=1) + timedelta(days=32)).replace(day=1))
        ax.plot(grade_stats.dates, grade_stats.climbs, label=grade)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='xx-small')

    ax.set_ylim(bottom=0)
    ax.tick_params(axis='x', labelsize='xx-small', labelrotation=20, pad=0)
    ax.set_xlim(first_day, last_day)

plt.subplots_adjust(hspace=0.5)
plt.show()
