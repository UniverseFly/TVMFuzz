from matplotlib import pyplot as plt
import argparse
import pickle

parser = argparse.ArgumentParser()
parser.add_argument('--cov-file', type=str, required=True)
args = parser.parse_args()

with open(args.cov_file, 'rb') as f:
    data = pickle.load(f)

xs = [time for time, cov in data]
ys = [cov  for time, cov in data]

plt.plot(xs, ys)
plt.xlabel('Time (seconds)')
plt.ylabel('Coverage #')

plt.savefig('cov.pdf')
plt.savefig('cov.png')
print('Figure saved: cov.pdf & cov.png')
