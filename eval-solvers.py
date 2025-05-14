#! /usr/bin/python3

# This script evaluates the performance of a given set of solvers in a given challenge.
#
# For each instance, the script retrieves the objective value of the best solution
# in order to compute, for each given solver, a penalty between 0 and 1 (using feature
# scaling) where 0 means the solution is one of the best and 1 means it is one of the
# worst. (In case there is no solution, the penalty is 1.)
#
# In the end the script prints, for each given solver, the number of instances it failed on,
# and the penalties in terms of their mean, standard deviation, and median.
#
# The database is expected to reside in the working directory under the name results.db.
#
# Notice that the result of evaluation does not depend on the given set of solvers but
# only on the contents of the database.

import argparse
import json
import numpy
import sqlite3
import statistics
import sys

def evalSolvers(cursor, year, solvers, verbose):
    jobs = list(cursor.execute('SELECT DISTINCT result.problem, problem.type, result.instance FROM result JOIN problem ON result.problem = problem.name WHERE result.year = ? ORDER BY result.problem, result.instance', (year,)));
    if not jobs:
        print('There are no results for challenge {}'.format(year), file = sys.stderr)
        return {}
    allSolvers = list(map(lambda result: result[0], cursor.execute('SELECT DISTINCT result.solver from result WHERE result.year = ?', (year,))));
    results = {}
    penalties = {}
    failures = {}
    for solver in allSolvers:
        results[solver] = list(cursor.execute('SELECT solved, objective_value FROM result WHERE year = ? AND solver = ? ORDER BY problem, instance', (year, solver)))
        if len(results[solver]) != len(jobs):
            print('Expected {} results for solver {}, but found {}'.format(len(jobs), solver, len(results[solver])), file = sys.stderr)
            return {}
    for solver in solvers:
        penalties[solver] = []
        failures[solver] = 0
    for i in range(0, len(jobs)):
        (problem, problem_type, instance) = jobs[i]
        objectiveValues = list(map(lambda result: result[1], filter(lambda result: result[0] and result[1], [results[solver][i] for solver in allSolvers])))
        (minObjectiveValue, maxObjectiveValue) = (None, None) if not objectiveValues else (min(objectiveValues), max(objectiveValues))
        if verbose:
            print('-' * 80)
            print(problem, problem_type, instance, minObjectiveValue, maxObjectiveValue)
        for solver in solvers:
            (solved, objectiveValue) = results[solver][i]
            if solved:
                if maxObjectiveValue == minObjectiveValue:
                    penalty = 0
                elif problem_type == 'MIN':
                    penalty = (objectiveValue - minObjectiveValue) / (maxObjectiveValue - minObjectiveValue)
                else:
                    penalty = 1 - ((objectiveValue - minObjectiveValue) / (maxObjectiveValue - minObjectiveValue))
                if verbose:
                    print(solver, objectiveValue, penalty)
            else:
                failures[solver] += 1
                penalty = 1
            penalties[solver] += [penalty]
    return {solver: {'failures': failures[solver], 'penalties': penalties[solver]} for solver in solvers}

def postprocessResult(result):
    penalties = result['penalties']
    return {
        'failures': result['failures'],
        'penalty-min': min(penalties),
        'penalty-max': max(penalties),
        'penalty-mean': statistics.mean(penalties),
        'penalty-pstdev': statistics.pstdev(penalties),
        'penalty-median': statistics.median(penalties),
        'penalty-histogram': numpy.histogram(penalties, 10, (0, 1))[0].tolist()
    }

def main():
    parser = argparse.ArgumentParser(description = 'Evaluates the performance of the given solvers in the given challenge')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('years', metavar = 'year', nargs = 1)
    parser.add_argument('solvers', metavar = 'solver', nargs = '+')
    args = parser.parse_args()
    with sqlite3.connect("results.db") as conn:
        cursor = conn.cursor()
        results = evalSolvers(cursor, args.years[0], args.solvers, args.verbose)
        if results:
            postprocessedResults = {solver: postprocessResult(results[solver]) for solver in results}
            print(json.dumps(postprocessedResults, sort_keys = True, indent = 4))

main()
