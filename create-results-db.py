#! /usr/bin/python3

# This script creates a database of results from MiniZinc challenges (results.db).
# To import results, call the script with a list of JSON result files on the command line.
# When the database already exists, the given results will be added unless they are
# already in the database.

import argparse
import json
import sqlite3
from itertools import repeat

def createDb(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS problem (name TEXT PRIMARY KEY ON CONFLICT IGNORE, kind TEXT NOT NULL CONSTRAINT problem_kind_constraint CHECK (kind IN ("MIN", "MAX", "SAT"))) WITHOUT ROWID')
    cursor.execute('CREATE TABLE IF NOT EXISTS solver (name TEXT PRIMARY KEY ON CONFLICT IGNORE, fd INT NOT NULL CONSTRAINT solver_fd_constraint CHECK (fd in (0, 1)), free INT NOT NULL CONSTRAINT solver_free_constraint CHECK (free in (0, 1)), par INT NOT NULL CONSTRAINT solver_par_constraint CHECK (par in (0, 1)), open INT NOT NULL CONSTRAINT solver_open_constraint CHECK (open in (0, 1))) WITHOUT ROWID')
    cursor.execute('CREATE TABLE IF NOT EXISTS result (challenge INT NOT NULL, solver TEXT REFERENCES solver NOT NULL, problem TEXT REFERENCES problem NOT NULL, instance TEXT NOT NULL, solved INT NOT NULL CONSTRAINT result_solved_constraint CHECK (solved in (0, 1)), complete INT NOT NULL CONSTRAINT result_complete_constraint CHECK (complete in (0, 1)), time INT NOT NULL, quality INT, CONSTRAINT result_unique_constraint UNIQUE (challenge, solver, problem, instance) ON CONFLICT IGNORE)')
    cursor.execute('CREATE INDEX IF NOT EXISTS solver_index ON solver(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS result_challenge_index ON result(challenge)')
    cursor.execute('CREATE INDEX IF NOT EXISTS result_solver_index ON result(solver)')
    cursor.execute('CREATE INDEX IF NOT EXISTS result_index ON result(challenge, solver, problem, instance)')

# YACS was renamed to Yuck
def fixedSolverName(solver):
    return 'Yuck-free' if solver == 'YACS-free' else 'Yuck-par' if solver == 'YACS-par' else solver

# state -> (solved, complete)
stateDict = {
    'SC': (True,  True),
    'S':  (True,  False),
    'S ': (True,  False),
    'SU': (True,  False),
    'C':  (False, True),
    ' C': (False, True),
    'UC': (False, True),
    'UU': (False, False),
    '  ': (False, False),
    'UNK': (False, False),
    'UNKNOWN': (False, False),
    'E': (False, False),
    'ERR': (False, False),
    'ERROR Incorrect': (False, False),
    'MZN': (False, False),
    'INC': (False, False)
}

def importResults(file, cursor):
    results = json.load(file)
    year = results['year']
    solvers = list(map(fixedSolverName, results['solvers']))
    problems = results['problems']
    benchmarks = results['benchmarks']
    cursor.executemany(
        'INSERT INTO solver VALUES(?, ?, ?, ?, ?)',
        zip(solvers, results['fd_solvers'], results['free_solvers'], results['par_solvers'], results['open_solvers']))
    cursor.executemany('INSERT INTO problem VALUES(?, ?)', zip(problems, results['kind']))
    jobs = [(problem, instance)
            for (problem, instances) in zip(problems, map(lambda refs: map(lambda ref: benchmarks[ref], refs), results['instances']))
            for instance in instances]
    for (solver, states, times, objectives) in zip(solvers, results['results'], results['times'], results['objectives']):
         cursor.executemany(
             'INSERT INTO result VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
             zip(repeat(year, len(jobs)),
                 repeat(solver, len(jobs)),
                 map(lambda job: job[0], jobs), # problem
                 map(lambda job: job[1], jobs), # instance
                 map(lambda state: stateDict[state][0], states), # solved
                 map(lambda state: stateDict[state][1], states), # complete
                 times,
                 objectives))

def main():
    parser = argparse.ArgumentParser(description = 'Puts MiniZinc challenge results into database')
    parser.add_argument('filenames', metavar = 'json-result-file', nargs = '+')
    args = parser.parse_args()
    with sqlite3.connect("results.db") as conn:
        cursor = conn.cursor()
        createDb(cursor)
        cursor.execute('PRAGMA foreign_keys = ON');
        for filename in args.filenames:
            with open(filename) as file:
                importResults(file, cursor)
                conn.commit()

main()
