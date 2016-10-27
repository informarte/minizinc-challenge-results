compare-yuck-to-oscar-in-2016:
	./compare-solvers.py 2016 'Yuck-free' 'OscaR/CBLS-free'

compare-local-search-solvers-to-best-free-solvers-in-2016:
	./compare-solvers.py 2016 'Picat SAT-free' 'Yuck-free' 'OscaR/CBLS-free' 'HaifaCSP-free' 'iZplus-free'
