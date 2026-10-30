import sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mcad import *

R = {}  # численные результаты для отчёта


def fmt(v, n=3):
    return [round(float(a), n) for a in np.atleast_1d(v)]


def run(tag, x, y, xs, ys, xd, yd, u, g_exp, pm, pn):
    """tag — 'z1' (данные примеров) или 'z2' (вариант 4).
    x, y — основные данные; xs, ys — данные для сглаживания; xd, yd — для устранения тренда."""
    r = R[tag] = {}
    t = np.linspace(x[0] - (2 if tag == 'z1' else 1), x[-1] + 1, 400)
    ti = np.linspace(x[0], x[-1] + 1, 300)

    # ---- Интерполяция (рис. 3.2 – 3.5)
    fig, ax = plt.subplots(2, 2, figsize=(10, 7.5))
    a = ax[0, 0]; a.plot(x, y, 'ro', mfc='none'); a.plot(ti, linterp(x, y, ti), 'b-')
    a.set_title('linterp(x, y, t)')
    a = ax[0, 1]; f = spline('c', x, y); a.plot(x, y, 'ro', mfc='none'); a.plot(ti, f(ti), 'b-')
    a.set_title('s := cspline(x, y), interp(s, x, y, t)')
    a = ax[1, 0]
    for k, c, nm in (('c', 'k', 'cspline'), ('p', 'm', 'pspline'), ('l', 'b', 'lspline')):
        a.plot(t, spline(k, x, y)(t), c + '-', label=nm)
    a.plot(x, y, 'ro', mfc='none', label='точки x, y'); a.legend(fontsize=8)
    a.set_title('Сплайны вблизи конечных точек')
    r['spl_ends'] = {k: fmt([spline(k, x, y)(t[0]), spline(k, x, y)(t[-1])], 2) for k in 'cpl'}
    a = ax[1, 1]; fb = bspline(x, y, u, 2); tb = np.linspace(u[0], u[-1], 400)
    a.plot(x, y, 'ro', mfc='none'); a.plot(tb, fb(tb), 'b-')
    a.set_title('s := bspline(x, y, u, 2), interp(s, x, y, t)')
    for a in ax.flat: a.grid(alpha=.4); a.set_xlabel('x, t')
    fig.tight_layout(); fig.savefig(f'{tag}_interp.png', dpi=150); plt.close(fig)

    # ---- Предсказание (рис. 3.6)
    fig, a = plt.subplots(figsize=(8, 3.6))
    if tag == 'z1':
        k = 100; j = np.arange(k + 1); yp = np.exp(-j / 100) * np.sin(j / 10); m, n = 50, 150
    else:
        j = np.arange(len(y)); yp = y; m, n = pm, pn
    fp = predict(yp, m, n)
    a.plot(j, yp, 'b-o' if tag == 'z2' else 'b-', ms=4, label='y')
    a.plot(np.arange(len(yp), len(yp) + n), fp, 'ro', mfc='none', ms=4, label=f'predict(y, {m}, {n})')
    a.legend(); a.grid(alpha=.4); a.set_xlabel('j')
    r['predict'] = fmt(fp[:10], 2)
    fig.tight_layout(); fig.savefig(f'{tag}_predict.png', dpi=150); plt.close(fig)

    # ---- Регрессия (рис. 3.8 – 3.11)
    fig, ax = plt.subplots(2, 2, figsize=(10, 7.5))
    L = line(x, y); M = medfit(x, y)
    f1 = lambda s: L[0] + L[1] * s
    r['line'] = fmt(L); r['medfit'] = fmt(M); r['d_line'] = round(delta(y, f1(x)), 4)
    a = ax[0, 0]; a.plot(x, y, 'ro', mfc='none'); a.plot(ti, f1(ti), 'b-')
    a.set_title(f'line(x,y) = ({L[0]:.3f}; {L[1]:.3f}),  Δ = {r["d_line"]}')
    a = ax[0, 1]; a.plot(x, y, 'ro', mfc='none'); a.plot(ti, f1(ti), 'b-', label='f1(t) (line)')
    a.plot(ti, M[0] + M[1] * ti, ':', c='brown', lw=2, label='g(t) (medfit)'); a.legend(fontsize=8)
    a.set_title(f'medfit(x,y) = ({M[0]:.3f}; {M[1]:.3f})')
    a = ax[1, 0]; a.plot(x, y, 'ro', mfc='none')
    for k, c in ((1, 'b'), (2, 'r'), (3, 'g')):
        fk = regress(x, y, k); r[f'd_reg{k}'] = round(delta(y, fk(x)), 4)
        a.plot(ti, fk(ti), c + '-', label=f'k={k}, Δ{k} = {r[f"d_reg{k}"]}')
    a.legend(fontsize=8); a.set_title('regress(x, y, k), k = 1, 2, 3')
    a = ax[1, 1]; fl = loess(x, y, 0.9); tl = np.linspace(x[0], x[-1], 300)
    r['d_loess'] = round(delta(y, fl(x)), 4)
    a.plot(x, y, 'ro', mfc='none'); a.plot(tl, fl(tl), 'b-')
    a.set_title(f'loess(x, y, 0.9),  Δ = {r["d_loess"]}')
    for a in ax.flat: a.grid(alpha=.4); a.set_xlabel('x, t')
    fig.tight_layout(); fig.savefig(f'{tag}_regr.png', dpi=150); plt.close(fig)

    # ---- Специальная регрессия (рис. 3.13 – 3.15)
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
    C = expfit(x, y, g_exp); fe = lambda s: C[0] * np.exp(C[1] * s) + C[2]
    r['expfit'] = fmt(C); r['d_exp'] = round(delta(y, fe(x)), 4); r['g_exp'] = g_exp
    a = ax[0]; a.plot(x, y, 'ro', mfc='none'); a.plot(ti, fe(ti), 'b-')
    a.set_title(f'expfit: C = ({C[0]:.3f}; {C[1]:.3f}; {C[2]:.3f})\nΔ = {r["d_exp"]}', fontsize=10)
    F = lambda s: np.array([1 / (s + 1), s, np.exp(s)])
    Cl = linfit(x, y, F); fl = lambda s: Cl[0] / (s + 1) + Cl[1] * s + Cl[2] * np.exp(s)
    r['linfit'] = fmt(Cl, 5); r['d_linfit'] = round(delta(y, fl(x)), 4)
    a = ax[1]; a.plot(x, y, 'ro', mfc='none'); a.plot(ti, fl(ti), 'b-')
    a.set_title(f'linfit(x, y, F)\nΔ = {r["d_linfit"]}', fontsize=10)
    with np.errstate(divide="ignore"):
        cg = genfit(x, y, [2, 2], lambda s, A, b: A * s**b); r['genfit'] = fmt(cg)
    r['d_genfit'] = round(delta(y, cg[0] * x**cg[1]), 4)
    a = ax[2]; a.plot(x, y, 'ro', mfc='none'); a.plot(ti, cg[0] * ti**cg[1], 'b-')
    a.set_title(f'genfit: A = {cg[0]:.3f}, b = {cg[1]:.3f}\nΔ = {r["d_genfit"]}', fontsize=10)
    for a in ax.flat: a.grid(alpha=.4); a.set_xlabel('x, t')
    fig.tight_layout(); fig.savefig(f'{tag}_spec.png', dpi=150); plt.close(fig)

    # ---- Сглаживание и устранение тренда (рис. 3.16 – 3.20)
    fig, ax = plt.subplots(3, 2, figsize=(10, 10))
    z = supsmooth(xs, ys); fz = spline('c', xs, z); tz = np.linspace(xs[0], xs[-1], 300)
    a = ax[0, 0]; a.plot(xs, ys, 'ko-', mfc='none', lw=.8); a.plot(xs, z, 'ro', tz, fz(tz), 'r-')
    a.set_title('z := supsmooth(x, y), cspline + interp')
    a = ax[0, 1]; a.plot(xs, ys, 'ko-', mfc='none', lw=.8, label='y')
    a.plot(xs, medsmooth(ys, 3), 'b-', label='medsmooth(y, 3)')
    a.plot(xs, medsmooth(ys, 7), 'r--', label='medsmooth(y, 7)'); a.legend(fontsize=8)
    a.set_title('Бегущие медианы')
    a = ax[1, 0]; a.plot(xs, ys, 'ko-', mfc='none', lw=.8, label='y')
    a.plot(xs, ksmooth(xs, ys, 2), 'b-', label='ksmooth(x, y, 2)')
    a.plot(xs, ksmooth(xs, ys, 5), 'r--', label='ksmooth(x, y, 5)'); a.legend(fontsize=8)
    a.set_title('Сглаживание функцией Гаусса')
    mavg = moving_average(ys, 3)
    a = ax[1, 1]; a.plot(xs, ys, 'ko', mfc='none', label='y'); a.plot(xs, mavg, 'b-', label='m (w = 3)')
    a.legend(fontsize=8); a.set_title('Скользящее усреднение, w = 3')
    Ld = line(xd, yd); md = yd - (Ld[0] + Ld[1] * xd)
    r['detrend_line'] = fmt(Ld)
    a = ax[2, 0]; a.plot(xd, yd, 'ko', mfc='none', label='y'); a.plot(xd, Ld[0] + Ld[1] * xd, 'b--', label='f(x) — тренд')
    a.plot(xd, md, 'r-', label='m = y − f(x)'); a.legend(fontsize=8); a.set_title('Устранение тренда')
    ax[2, 1].axis('off')
    for a in ax.flat[:5]: a.grid(alpha=.4); a.set_xlabel('x')
    fig.tight_layout(); fig.savefig(f'{tag}_smooth.png', dpi=150); plt.close(fig)
    r['z'] = fmt(z, 2); r['med3'] = fmt(medsmooth(ys, 3), 2); r['k2'] = fmt(ksmooth(xs, ys, 2), 2)
    r['mavg'] = fmt(mavg, 2); r['detrend'] = fmt(md, 2)


# Задание 1 — данные из примеров методички
x1 = np.arange(7.0); y1 = np.array([4.1, 2.4, 3, 4.3, 3.6, 5.2, 5.9])
xs1 = np.arange(17.0)
ys1 = np.array([4.1, 2.4, 3, 4.3, 3.6, 5.2, 5.9, 5, 4.7, 4, 3.5, 3.9, 3, 2.7, 3.7, 4.8, 5.4])
yd1 = np.array([5.1, 4.4, 5.7, 5.3, 5.6, 5.2, 5.9, 7.7, 6.7, 7, 6.5, 5.9, 8.1, 8.7, 9.7, 9.8, 10.4])
run('z1', x1, y1, xs1, ys1, xs1, yd1, [-0.5, 2.2, 3.3, 4.1, 5.5, 7], [1, 1, 1], 50, 150)

# Задание 2 — вариант 4: y := ceil(m·rchisq(n, d)), d = 5, m = 1, n = 11
rng = np.random.default_rng(4)
x2 = np.arange(11.0); y2 = np.ceil(1 * rng.chisquare(5, 11))
R['y2'] = y2.astype(int).tolist()
run('z2', x2, y2, x2, y2, x2, y2, [-0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 10.5], [5, -0.5, 3], 5, 5)

json.dump(R, open('res3.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False))
