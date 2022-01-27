# minizinc-challenge-results
Tools to build and query a database of MiniZinc challenge results

The aim of this project is to provide tools to investigate the results of the [MiniZinc challenges](http://www.minizinc.org/challenge.html).

Currently there are two Python scripts:

* `create-results-db.py` creates an Sqlite database of results from MiniZinc challenges (`results.db`). To import results, call the script with a list of JSON result files (see below) on the command line. When the database already exists, the given results will be added unless they are already in the database.

* `compare-solvers.py` compares the performance of given solvers in a given challenge by looking at the objective values the competitors achieved. (Runtime and proof of optimality do not play a role here.) For each solver and each instance, the script computes a penalty; the worse a result in comparison to the best result, the higher the penalty. (Please see the script for the details of penalization.) In the end, the script prints the penalties in terms of their mean, standard deviation, and median.

The `results` folder contains the MiniZinc challenge results from 2011 to 2021; for each year, there is a JSON file. (This data was extracted from the JavaScript files used by the MiniZinc web site.) The files contain all the data except for the scores.

To generate a JSON file for import into the database, proceed as follows:

* Download the results from the MiniZinc web site, e.g. http://www.minizinc.org/challenge2016/results.js.
* Append this snippet:

```
function writeJson(results) {
    var fs = require('fs');
    fs.writeFile(
        "results.json",
        JSON.stringify(results, null, 2),
        function(err, result) {
            if(err) console.log('error', err);
        });
}

var year = 2021

if (year < 2021) {
    writeJson({
        "year": year,
        "solvers": solvers,
        "fd_solvers": fd_solvers,
        "free_solvers": free_solvers,
        "par_solvers": par_solvers,
        "open_solvers": open_solvers,
        "problems": problems,
        "kind": kind,
        "instances": instances,
        "benchmarks": benchmarks,
        "results": results,
        "times": times,
        "objectives": objectives
    });
} else {
    with (json.results) writeJson({
        "year": year,
        "solvers": solvers,
        "fd_solvers": fd_solvers,
        "free_solvers": free_solvers,
        "par_solvers": par_solvers,
        "open_solvers": open_solvers,
        "problems": problems,
        "kind": kind,
        "instances": instances,
        "benchmarks": benchmarks,
        "results": results,
        "times": times,
        "objectives": objectives
    });
}
```

* Update the year.
* Run the resulting script with `nodejs`.
