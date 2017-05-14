#!/usr/bin/python2.7
"""
    pe-analysis.py - tool for personal expense analysis.

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

import argparse
import sys

import expense_from_seb_csv
import expense_from_seb_xlsx
import analyse

def mkenv():
    parser = argparse.ArgumentParser(add_help=True, version='0.2',
                                     description="Personal expense analysis.")
    parser.add_argument("file", type=str, action="store",
                        help="Path to file with expense data.")
    return parser.parse_args()

def main():
    env = mkenv()
    e = expense_from_seb_xlsx.expense_reader(env.file)
    #e = expense_from_csv.expense_reader(env.file)
    e.sort(key=lambda x: x.date, reverse=False)
    analyse.optimize(e)
    analyse.category_analysis(e)
    analyse.comparative_analysis(e)

if __name__ == "__main__":
    sys.exit(main())
