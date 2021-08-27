import argparse
import os
import pickle
from typing import List, Tuple
from tvm import tir
import tvm
from tvm.contrib import coverage as memcov
import multiprocessing as mp

parser = argparse.ArgumentParser()
parser.add_argument('--report-folder', type=str, required=True, help='Folder having saved TIRs')
parser.add_argument('--building-timeout', type=float, default=600, help='Building timeout (seconds)')
args = parser.parse_args()

TIMEOUT: float = args.building_timeout
REPORT_FOLDER = os.path.join(os.getcwd(), args.report_folder)

def build(func, d):
    memcov.set_hitmap(d['hitmap'])
    memcov.set_now(d['now'])
    tvm.build(func)
    d['ret_hitmap'] = memcov.get_hitmap()
    d['ret_now'] = memcov.get_now()

if __name__ == '__main__':
    files_int = sorted([int(f[:-4]) for f in os.listdir(REPORT_FOLDER) if f.endswith('.mod')])
    files = [os.path.join(REPORT_FOLDER, f'{f}.mod') for f in files_int]

    error_count = 0
    memcov.reset()
    now = memcov.get_now()
    hitmap = memcov.get_hitmap()
    cov_data: List[Tuple[float, int]] = []
    for fname in files:
        print(f"Processing {fname}")
        with open(fname, 'rb') as f:
            data: List[Tuple[float, tvm.IRModule]] = pickle.load(f)
        for time, func in data:
            with mp.Manager() as m:
                d = m.dict()
                d['hitmap'] = hitmap
                d['now'] = now
                p = mp.Process(target=build, args=(func, d))
                p.start()
                p.join(TIMEOUT)
                if p.is_alive() or p.exitcode != 0:
                    p.terminate()
                    error_count += 1
                    print(f"Error #{error_count}")
                    continue
                else:
                    memcov.set_now(d['ret_now'])
                    memcov.set_hitmap(d['ret_hitmap'])
                    now = memcov.get_now()
                    hitmap = memcov.get_hitmap()
            cov_data.append((time, memcov.get_now()))
            print(cov_data[-1], end='\r')
    cov_file = os.path.join(REPORT_FOLDER, f'cov.pickle')
    with open(cov_file, 'wb') as f:
        pickle.dump(cov_data, f)
    print(f'Coverage saved to {cov_file}')
