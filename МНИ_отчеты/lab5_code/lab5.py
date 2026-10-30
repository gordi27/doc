import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ce import curvefinder, lagrange

# Вариант 4 (Приложение А)
x = np.round(np.arange(0, 1.2, 0.1), 1)
y = np.array([1.27, 2.25, 3.85, 4.45, 5.95, 6.12, 4.33, 3.78, 3.76, 2.53, 1.46, 1.19])
t = np.linspace(0, 1.1, 400)

# п. 2–4: CurveFinder, все модели, порядок полинома 4
res = curvefinder(x, y, 4)
for k, (name, formula, c, S, r, f) in enumerate(res, 1):
    print(f"{k:2d} {name:28s} S = {S:.4f}  r = {r:.4f}  {formula}  coef = {np.round(c, 5)}")
best = res[0]

# п. 5: интерполяционный полином Лагранжа (степень 11)
L = lagrange(x, y)
P = lambda s: np.polyval(L[::-1], s)
print("Lagrange coefs (a0..a11):", [f"{v:.4e}" for v in L])
print("max |P(x_i) - y_i| =", np.max(np.abs(P(x) - y)))

# п. 6: модель, выбранная вручную (Apply Fit) — Gaussian Model
gauss = [q for q in res if q[0] == 'Gaussian Model'][0]

def plot(fname, curve, label, title):
    fig, a = plt.subplots(figsize=(7.5, 4.3))
    a.plot(x, y, 'bo', ms=5, label='данные (вариант 4)')
    a.plot(t, curve(t), 'r-', label=label)
    a.set_title(title, fontsize=10); a.set_xlabel('X'); a.set_ylabel('Y')
    a.grid(alpha=.4); a.legend(fontsize=8); fig.tight_layout(); fig.savefig(fname, dpi=150); plt.close(fig)

plot('best.png', lambda s: best[5](s, *best[2]), best[0],
     f'{best[0]}: {best[1]};  S = {best[3]:.4f}, r = {best[4]:.4f}')
plot('lagr.png', P, 'полином Лагранжа 11-й степени', 'Polynomial Interpolation')
plot('gauss.png', lambda s: gauss[5](s, *gauss[2]), 'Gaussian Model',
     f'Apply Fit → Gaussian Model: {gauss[1]};  S = {gauss[3]:.4f}, r = {gauss[4]:.4f}')

json.dump({'rank': [(q[0], q[1], [float(v) for v in q[2]], float(q[3]), float(q[4])) for q in res],
           'lagr': [float(v) for v in L]}, open('res5.json', 'w'), ensure_ascii=False, indent=1)
