#! /usr/bin/python3

# This script compares the performance of a given set of solvers in a given challenge.
# For each instance, the script retrieves the objective value of the best solution
# in order to compute, for each solver S, a penalty in terms of how much worse the
# solution of S was in comparison to the best solution.

# For example, say we are considering an instance of a minimization problem,
# the best solution's objective value was 100, and the solver S produced a solution
# of quality 105. Then S is given a penalty of (105 - 100) / 100 = 0.05 (5%). 
# In case the best solution has quality 0, the following approach applies:
# The penalty is computed on a scale between 0 and 1 where 0 means the solution is one
# of the best and 1 means the solution is one of the worst.

# In the end the script prints, for each solver, the number of instances it failed on,
# and the penalties in terms of their mean, standard deviation, median, and mode.

# The database is expected to reside in the working directory under the name results.db.

import argparse
import json
import sqlite3
import statistics
import sys

def compareSolvers(cursor, challenge, solvers, verbose):
    jobs = list(cursor.execute('SELECT DISTINCT result.problem, problem.kind, result.instance FROM result JOIN problem ON result.problem = problem.name WHERE result.challenge = ? ORDER BY result.problem, result.instance', (challenge,)));
    if not jobs:
        print('There are no results for challenge {}'.format(challenge), file = sys.stderr)
        return {}
    results = {}
    penalties = {}
    failures = {}
    for solver in solvers:
        results[solver] = list(cursor.execute('SELECT solved, quality FROM result WHERE challenge = ? AND solver = ? ORDER BY problem, instance', (challenge, solver)))
        if len(results[solver]) != len(jobs):
            print('Expected {} results for solver {}, but found {}'.format(len(jobs), solver, len(results[solver])), file = sys.stderr)
            return {}
        penalties[solver] = []
        failures[solver] = 0
    for i in range(0, len(jobs)):
        (problem, kind, instance) = jobs[i]
        qualities = list(map(lambda result: result[1], filter(lambda result: result[0], [results[solver][i] for solver in solvers])))
        (low, high) = (None, None) if not qualities else (min(qualities), max(qualities))
        if verbose:
            print('-' * 80)
            print(problem, instance, kind, low, high)
        for solver in solvers:
            (solved, quality) = results[solver][i]
            if solved:
                if high == low:
                    penalty = 0
                elif kind == 'MIN':
                    penalty = (quality - low) / abs(low) if low != 0 else (quality - low) / (high - low)
                else:
                    penalty = (high - quality) / abs(high) if high != 0 else  (high - quality) / (high - low)
                penalties[solver] += [penalty]
                if verbose:
                    print(solver, quality, penalty)
            else:
                failures[solver] += 1
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
        'penalty-mode': statistics.mode(penalties)
    }

def main():
    parser = argparse.ArgumentParser(description = 'Compares the performance of the given solvers in the given challenge')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('challenges', metavar = 'challenge', nargs = 1)
    parser.add_argument('solvers', metavar = 'solver', nargs = '+')
    args = parser.parse_args()
    with sqlite3.connect("results.db") as conn:
        cursor = conn.cursor()
        results = compareSolvers(cursor, args.challenges[0], args.solvers, args.verbose)
        if results:
            postprocessedResults = {solver: postprocessResult(results[solver]) for solver in results}
            print(json.dumps(postprocessedResults, sort_keys = True, indent = 4))

main()
