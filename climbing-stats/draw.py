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

with open(stats_file, 'r', encoding='utf8') as f:
    stats = json.load(f)

class Climb():
    style: str
    grade: str
    result: str

    def __init__(self, stats):
        for key, value in stats.items():
            if key != "name":
                self.grade = key
                self.result = value

    def __repr__(self):
        return f'{self.style}({self.grade}, {self.result})'

    def flash(self):
        return self.result == 'flash'

class Boulder(Climb):
    style = 'Bouldering'

class Moon(Climb):
    style = 'Moonboard'

class TopRope(Climb):
    style = 'Top-rope'

class Lead(Climb):
    style = 'Lead'

class ClimbingSession():
    place: str
    date: str
    climbs: list[Climb]
    bouldering: list[Boulder]
    lead: list[Lead]
    top_rope: list[TopRope]
    moon: list[Moon]

    def __init__(self, stats):
        for key, value in stats.items():
            setattr(self, key, ClimbingSession.get_value(key, value))

        self.climbs = []
        self.styles = []
        if hasattr(self, 'bouldering'):
            self.styles.append('Bouldering')
            self.climbs.extend(self.bouldering)
        if hasattr(self, 'top-rope'):
            self.top_rope = getattr(self, 'top-rope')
            self.styles.append('Top Rope')
            self.climbs.extend(self.top_rope)
        if hasattr(self, 'lead'):
            self.styles.append('Lead')
            self.climbs.extend(self.lead)
        if hasattr(self, 'moon'):
            self.styles.append('moon')
            self.climbs.extend(self.moon)

        assert len(self.styles) != 0

    @staticmethod
    def get_value(key, value):
        ret = []
        if key == 'bouldering':
            for c in value:
                ret.append(Boulder(c))
        elif key == 'top-rope':
            for c in value:
                ret.append(TopRope(c))
        elif key == 'lead':
            for c in value:
                ret.append(Lead(c))
        elif key == 'moon':
            for c in value:
                ret.append(Moon(c))
        else:
            return value
        return ret

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

sessions: list[ClimbingSession] = []
for s in stats:
    sessions.append(ClimbingSession(s))

def plot_data(sessions: list[ClimbingSession], style: str):
    flash: dict[str, int] = {}
    redpoint: dict[str, int] = {}
    for s in sessions:
        for c in s.climbs:
            if c.style == style:
                if c.grade not in flash:
                    flash[c.grade] = 0
                    redpoint[c.grade] = 0

                d = flash if c.flash() else redpoint
                d[c.grade] += 1

    flash = OrderedDict(sorted(flash.items()))
    redpoint = OrderedDict(sorted(redpoint.items()))
    return (flash, redpoint)

figure, axis = plt.subplots(1, 2)

(f, r) = plot_data(sessions, 'Moonboard')
axis[0].bar(f.keys(), f.values(), color='green')
axis[0].bar(r.keys(), r.values(), color='orange', bottom=list(f.values()))

(f, r) = plot_data(sessions, 'Bouldering')
axis[1].bar(f.keys(), f.values(), color='green')
axis[1].bar(r.keys(), r.values(), color='orange', bottom=list(f.values()))

plt.show()
