from pathlib import Path
from benchmark import run_benchmark
run_benchmark(Path('data/company.db'), Path('company_benchmark.json'))
