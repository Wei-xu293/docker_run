#!/usr/bin/env python3
import csv
import sys
import os
import math
import statistics
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read_diffs(path):
    rows = []
    with open(path, newline='') as f:
        r = csv.DictReader(f)
        for row in r:
            it = int(row['iter'])
            n = float(row['native_pss_mb'])
            d = float(row['docker_pss_mb'])
            diff = float(row['diff_mb'])
            pct = float(row['diff_percent'])
            rows.append((it,n,d,diff,pct))
    rows.sort()
    return rows

def plot_paired(rows, outdir):
    it = [r[0] for r in rows]
    native = [r[1] for r in rows]
    docker = [r[2] for r in rows]
    plt.figure(figsize=(10,6))
    for x,n,d in zip(it,native,docker):
        plt.plot([x,x],[n,d], color='0.8')
    plt.plot(it, native, marker='o', label='native')
    plt.plot(it, docker, marker='o', label='docker')
    plt.xlabel('iter')
    plt.ylabel('PSS (MB)')
    plt.title('Paired PSS (native vs docker)')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir,'paired_pss.png'), dpi=150)
    plt.close()

def plot_hist(rows, outdir):
    diffs = [r[3] for r in rows]
    plt.figure(figsize=(8,5))
    plt.hist(diffs, bins=12, color='#007acc', edgecolor='black')
    plt.xlabel('PSS difference (docker - native) [MB]')
    plt.ylabel('Count')
    plt.title('Histogram of PSS differences')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir,'diffs_hist.png'), dpi=150)
    plt.close()

def plot_box(rows, outdir):
    diffs = [r[3] for r in rows]
    plt.figure(figsize=(6,4))
    plt.boxplot(diffs, vert=True)
    plt.ylabel('PSS difference (MB)')
    plt.title('Boxplot of PSS differences')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir,'diffs_box.png'), dpi=150)
    plt.close()

def main():
    # Accept diffs.csv by default
    path = sys.argv[1] if len(sys.argv)>1 else 'diffs.csv'
    outdir = 'plots'
    Path(outdir).mkdir(parents=True, exist_ok=True)
    rows = read_diffs(path)
    if not rows:
        print('No rows found in', path)
        sys.exit(1)
    plot_paired(rows, outdir)
    plot_hist(rows, outdir)
    plot_box(rows, outdir)
    print('Plots saved to', outdir)

if __name__ == '__main__':
    main()
