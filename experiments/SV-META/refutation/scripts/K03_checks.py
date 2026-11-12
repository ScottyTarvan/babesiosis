"""K03 refutation checks: cell-free haemoglobin / haemolysis theme (T04). Seed 20261112."""
import json, sys
import numpy as np
from scipy import stats
ROOT = sys.argv[1]
rng = np.random.default_rng(20261112)
T = ROOT + '/experiments/shared/tidy/'

def cliff(a, b):
    a = np.asarray(a); b = np.asarray(b)
    return float((np.sign(a[:, None] - b[None, :])).mean())

def plex_perm(vals, lab, plex, n=20000):
    obs = cliff(vals[lab == 1], vals[lab == 0])
    cnt = 0
    for _ in range(n):
        l2 = lab.copy()
        for p in np.unique(plex):
            m = plex == p
            l2[m] = rng.permutation(l2[m])
        if abs(cliff(vals[l2 == 1], vals[l2 == 0])) >= abs(obs) - 1e-12:
            cnt += 1
    return obs, (cnt + 1) / (n + 1)

def boot(vals, lab, n=5000):
    a = vals[lab == 1]; b = vals[lab == 0]; out = []
    for _ in range(n):
        out.append(cliff(rng.choice(a, len(a)), rng.choice(b, len(b))))
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]

def rank_resid(y, x):
    ry = stats.rankdata(y); rx = stats.rankdata(x)
    b = np.polyfit(rx, ry, 1)
    return ry - np.polyval(b, rx)

res = {}
f = json.load(open(T + 'DS07.features.json')); o = json.load(open(T + 'DS07.outcomes.json'))
lab = {r['dog_id']: r['values']['complicated'] for r in o['records']}
P = {'hbb': 'p_p60524', 'ca2': 'p_f1pdy8', 'prdx2': 'p_f1pcg4', 'prdx6': 'p_f1pc59', 'hp': 'p_a0a5f4db38',
     'ltf': 'p_f1pr54', 'cd14': 'p_a0a1s7j0a8', 'ambp': 'p_j9nui6', 'alb': 'p_p49822'}
for v in f['variables']:
    if 'gene CD14' in v['original']: P['cd14'] = v['name']
rows = []
for r in f['records']:
    rows.append((r['dog_id'], lab.get(r['dog_id']), r['values']['plex'], {k: r['values'].get(c) for k, c in P.items() if c}))
inf = [x for x in rows if x[1] in (0, 1)]
ctl = [x for x in rows if x[1] is None]
def arr(sub, k):
    s = [x for x in sub if x[3].get(k) is not None]
    return (np.array([x[3][k] for x in s]), np.array([x[1] for x in s]), np.array([x[2] for x in s]), s)
for k in P:
    if not P[k]: continue
    v, l, p, s = arr(inf, k)
    if len(v) < 10: res[k] = {'n': len(v)}; continue
    obs, pp = plex_perm(v, l, p, 5000)
    d = {'n_comp': int((l == 1).sum()), 'n_unc': int((l == 0).sum()), 'cliff': round(obs, 3), 'p_plex_perm': round(pp, 4)}
    hv, hl, hp_, hs = arr(inf, 'hbb')
    common = [x for x in inf if x[3].get(k) is not None and x[3].get('hbb') is not None]
    if k != 'hbb':
        d['rho_with_hbb'] = round(float(stats.spearmanr([x[3]['hbb'] for x in common], [x[3][k] for x in common])[0]), 3)
    cv = [x[3][k] for x in ctl if x[3].get(k) is not None]
    d['median_comp'] = round(float(np.median(v[l == 1])), 3); d['median_unc'] = round(float(np.median(v[l == 0])), 3)
    d['median_ctrl'] = round(float(np.median(cv)), 3) if cv else None
    res[k] = d
# HBB detail
v, l, p, s = arr(inf, 'hbb')
res['hbb']['boot_ci'] = [round(x, 3) for x in boot(v, l)]
res['hbb']['unc_vs_ctrl_cliff'] = round(cliff(v[l == 0], np.array([x[3]['hbb'] for x in ctl if x[3].get('hbb') is not None])), 3)
srt = np.sort(v[l == 1])[::-1]
res['hbb']['comp_sorted'] = [round(float(x), 2) for x in srt]
res['hbb']['unc_sorted'] = [round(float(x), 2) for x in np.sort(v[l == 0])[::-1]]
res['hbb']['n_comp_above_unc_max'] = int((v[l == 1] > v[l == 0].max()).sum())
# drop top 3 complicated
keep = np.ones(len(v), bool); idx = np.argsort(-(v * (l == 1)))[:3]; keep[idx] = False
obs, pp = plex_perm(v[keep], l[keep], p[keep], 5000)
res['hbb']['drop_top3_comp'] = {'cliff': round(obs, 3), 'p': round(pp, 4)}
# HBB relative to RBC cytosolic markers (CA2, PRDX2): ratio = hbb - mean(ca2, prdx2) in log2
for adj in ['ltf', 'cd14', 'ca2', 'prdx2', 'hp', 'alb']:
    c = [x for x in inf if x[3].get(adj) is not None and x[3].get('hbb') is not None]
    y = np.array([x[3]['hbb'] for x in c]); xx = np.array([x[3][adj] for x in c])
    ll = np.array([x[1] for x in c]); pl = np.array([x[2] for x in c])
    rr = rank_resid(y, xx)
    obs, pp = plex_perm(rr, ll, pl, 5000)
    res['hbb']['adjusted_for_' + adj] = {'n': len(c), 'cliff': round(obs, 3), 'p': round(pp, 4)}
    if adj in ('ca2', 'prdx2', 'hp'):
        obs2, pp2 = plex_perm(y - xx, ll, pl, 5000)
        res['hbb']['log2_ratio_hbb_minus_' + adj] = {'cliff': round(obs2, 3), 'p': round(pp2, 4)}

# DS02
f2 = json.load(open(T + 'DS02.features.json')); o2 = json.load(open(T + 'DS02.outcomes.json'))
died = {r['dog_id']: r['values']['died'] for r in o2['records'] if 'died' in r['values']}
dogs = {}
for r in f2['records']:
    if r['post_treatment']: continue
    d = dogs.setdefault(r['dog_id'], {'dose': r['values'].get('dose_group'), 'cf': [], 'pa': [], 'hct': [], 'pairs': []})
    v = r['values']
    if v.get('cfhb') is not None: d['cf'].append(v['cfhb'])
    if v.get('parasitaemia_pct') is not None: d['pa'].append(v['parasitaemia_pct'])
    if v.get('hct') is not None: d['hct'].append(v['hct'])
    if v.get('cfhb') is not None and v.get('parasitaemia_pct'):
        d['pairs'].append((r['timepoint'], v['cfhb'], v['parasitaemia_pct'], v.get('hct')))
ds02 = {}
for k, d in dogs.items():
    ds02[k] = {'dose': d['dose'], 'died': died.get(k), 'cfhb_peak_mg_L': max(d['cf']), 'parasitaemia_peak_pct': max(d['pa']),
               'hct_first': d['hct'][0], 'hct_min_pretreat': min(d['hct']),
               'cfhb_per_pct_parasitaemia_sameday': [[t, round(c / pa, 1), round(pa, 2)] for t, c, pa, h in d['pairs'] if pa > 0.5]}
pk = [ds02[k]['cfhb_peak_mg_L'] for k in sorted(ds02)]; pp_ = [ds02[k]['parasitaemia_peak_pct'] for k in sorted(ds02)]
hd = [ds02[k]['hct_first'] - ds02[k]['hct_min_pretreat'] for k in sorted(ds02)]
res['ds02'] = {'dogs': ds02, 'spearman_cfhb_peak_vs_parasitaemia_peak': round(float(stats.spearmanr(pk, pp_)[0]), 3),
               'spearman_cfhb_peak_vs_hct_drop': round(float(stats.spearmanr(pk, hd)[0]), 3), 'n': len(pk)}
print(json.dumps(res, indent=1))
