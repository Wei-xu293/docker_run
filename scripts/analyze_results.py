#!/usr/bin/env python3
import csv
import sys
import statistics
import math
import random

def read_results(path):
    rows = []
    with open(path, newline='') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows

def to_float(x):
    try:
        return float(x)
    except:
        return None

def paired_stats(rows):
    native_pss = []
    docker_pss = []
    # assume rows alternate native,docker pairs or are ordered; group by iter
    by_iter = {}
    for row in rows:
        it = row['iter']
        by_iter.setdefault(it, {})
        if row['scenario'] == 'native':
            by_iter[it]['native'] = to_float(row.get('pss_mb',''))
        elif row['scenario'] == 'docker':
            # prefer host-side PSS if present
            val = to_float(row.get('docker_host_pss_mb',''))
            if val is None or val == 0.0:
                val = to_float(row.get('docker_pss_mb',''))
            by_iter[it]['docker'] = val

    diffs = []
    pairs = []
    for it, pair in sorted(by_iter.items(), key=lambda x:int(x[0])):
        n = pair.get('native')
        d = pair.get('docker')
        if n is None or d is None:
            continue
        pairs.append((n,d))
        diffs.append(d - n)

    return pairs, diffs

def mean_ci_bootstrap(diffs, n_boot=10000, alpha=0.05):
    if not diffs:
        return None
    means = []
    n = len(diffs)
    for _ in range(n_boot):
        sample = [random.choice(diffs) for _ in range(n)]
        means.append(statistics.mean(sample))
    means.sort()
    lo = means[int((alpha/2)*n_boot)]
    hi = means[int((1-alpha/2)*n_boot)]
    return statistics.mean(diffs), lo, hi

def paired_t_stat(diffs):
    n = len(diffs)
    if n < 2:
        return None
    m = statistics.mean(diffs)
    sd = statistics.pstdev(diffs) * math.sqrt(n/(n-1)) if n>1 else 0.0
    se = sd / math.sqrt(n)
    t = m / se if se>0 else float('inf')
    return t, m, sd

def bootstrap_pvalue(diffs, n_boot=10000):
    if not diffs:
        return None
    obs = statistics.mean(diffs)
    n = len(diffs)
    count = 0
    for _ in range(n_boot):
        sample = [random.choice(diffs) for _ in range(n)]
        if (statistics.mean(sample) >= obs):
            count += 1
    p = (count+1)/(n_boot+1)
    return p

def summarize(pairs, diffs):
    n = len(diffs)
    out = []
    out.append(f"pairs={n}")
    if n==0:
        out.append('No paired data found')
        return '\n'.join(out)
    mean, lo, hi = mean_ci_bootstrap(diffs)
    tstat = paired_t_stat(diffs)
    bp = bootstrap_pvalue(diffs)
    out.append(f"mean_diff_mb={mean:.4f}")
    out.append(f"95%CI_bootstrap_mb=[{lo:.4f}, {hi:.4f}]")
    out.append(f"bootstrap_p_ge_obs={bp:.4f} (one-sided p>=) ")
    if tstat:
        t, m, sd = tstat
        out.append(f"t_stat={t:.4f} mean={m:.4f} sd={sd:.4f}")
    # percent differences
    pct = [ (d / n * 100.0) if n!=0 else 0.0 for (n,d) in [(p[0], p[1]-p[0]) for p in pairs]]
    # compute mean percent
    pct_vals = [ (p[1]-p[0])/p[0]*100.0 for p in pairs if p[0]!=0]
    if pct_vals:
        out.append(f"mean_diff_percent={statistics.mean(pct_vals):.3f}")
    return '\n'.join(out)

def main():
    if len(sys.argv) < 2:
        print('Usage: analyze_results.py case1_simple_results.txt')
        sys.exit(2)
    rows = read_results(sys.argv[1])
    pairs, diffs = paired_stats(rows)
    report = summarize(pairs, diffs)
    with open('analysis_report.txt','w') as f:
        f.write(report + '\n')
    print(report)

if __name__ == '__main__':
    main()
