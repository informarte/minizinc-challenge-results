# minizinc-challenge-results

The aim of this project is to provide tools to investigate the results of the [MiniZinc challenges](http://www.minizinc.org/challenge.html).

Currently there are two Python scripts:

* `import-results.py` creates an Sqlite database of results from MiniZinc challenges (`results.db`). To import results, call the script with the year and the JSON result file on the command line. (Result files are available from https://github.com/MiniZinc/minizinc.github.io/tree/main/public/challenge). When the database already exists, the given results will be added unless they are already in the database.

* `eval-solvers.py` evaluates the performance of given solvers in a given challenge by looking at the objective values the competitors achieved. (Runtime and proof of optimality do not play a role here.) For each solver and each instance, the script computes a penalty; the worse a result in comparison to the best result, the higher the penalty. (Please see the script for the details of penalization.) In the end, the script prints the penalties in terms of their mean, standard deviation, and median.
