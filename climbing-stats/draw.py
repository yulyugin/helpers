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
    date: str
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

def plot_data(sessions: list[ClimbingSession], style: str):
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

figure, axis = plt.subplots(len(climbing_styles), 1)

for index, style in enumerate(climbing_styles):
    axis[index].set_title(f'{style} stats')
    (f, r) = plot_data(sessions, style)
    axis[index].bar(list(f.keys()), list(f.values()), color='green')
    axis[index].bar(list(r.keys()), list(r.values()), color='orange', bottom=list(f.values()))

plt.show()
