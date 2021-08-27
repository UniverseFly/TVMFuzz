import argparse
import subprocess
import os

parser = argparse.ArgumentParser()
parser.add_argument('--fuzz-time', type=float, required=True, help='Fuzzing time (minutes)')
parser.add_argument('--report-folder', type=str, required=True, help='Report folder')
parser.add_argument('--cov-tvm-home', type=str, required=True, help='Instrumented TVM_HOME')
parser.add_argument('--nocov-tvm-home', type=str, required=True, help='Non-instrumented TVM_HOME')
args = parser.parse_args()

COV_TVM_HOME: str = args.cov_tvm_home
NOCOV_TVM_HOME: str = args.nocov_tvm_home

cmd1 = f'PYTHONPATH={NOCOV_TVM_HOME}/python:$PYTHONPATH python src/run_tvmfuzz.py --fuzz-time {args.fuzz_time} --report-folder {args.report_folder}'
print(cmd1)
os.system(cmd1)

cmd2 = f'PYTHONPATH={COV_TVM_HOME}/python:$PYTHONPATH python src/save_cov.py --report-folder {args.report_folder}'
print(cmd2)
os.system(cmd2)

cmd3 = f"python src/plot_cov.py --cov-file {os.path.join(args.report_folder, 'cov.pickle')}"
print(cmd3)
os.system(cmd3)
