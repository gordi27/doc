"""Аналоги встроенных функций Mathcad, используемых в ЛР3."""
import numpy as np
from scipy.optimize import curve_fit


def linterp(x, y, t):
    """Кусочно-линейная интерполяция; за краями — продолжение крайних отрезков."""
    x, y, t = map(np.asarray, (x, y, t))
    i = np.clip(np.searchsorted(x, t) - 1, 0, len(x) - 2)
    return y[i] + (y[i + 1] - y[i]) * (t - x[i]) / (x[i + 1] - x[i])


def _spline_M(x, y, kind):
    """Вторые производные в узлах. kind: 'l' (lspline), 'p' (pspline), 'c' (cspline)."""
    n = len(x)
    h = np.diff(x)
    A = np.zeros((n, n)); r = np.zeros(n)
    for i in range(1, n - 1):
        A[i, i - 1:i + 2] = h[i - 1], 2 * (h[i - 1] + h[i]), h[i]
        r[i] = 6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])
    if kind == 'l':      # концы — линейные: M0 = Mn = 0
        A[0, 0] = A[-1, -1] = 1
    elif kind == 'p':    # концы — параболические: M0 = M1, Mn = Mn-1
        A[0, :2] = 1, -1; A[-1, -2:] = -1, 1
    else:                # концы — кубические: M экстраполируется линейно
        A[0, :3] = h[1], -(h[0] + h[1]), h[0]
        A[-1, -3:] = h[-1], -(h[-2] + h[-1]), h[-2]
    return np.linalg.solve(A, r)


def spline(kind, x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    M = _spline_M(x, y, kind)

    def f(t):
        t = np.asarray(t, float)
        i = np.clip(np.searchsorted(x, t) - 1, 0, len(x) - 2)
        h = x[i + 1] - x[i]; a = x[i + 1] - t; b = t - x[i]
        return (M[i] * a**3 + M[i + 1] * b**3) / (6 * h) + \
            (y[i] / h - M[i] * h / 6) * a + (y[i + 1] / h - M[i + 1] * h / 6) * b
    return f


def bspline(x, y, u, n):
    """Сплайн степени n со сшивкой в точках u, проходящий через (x, y)."""
    u = np.asarray(u, float)

    def basis(t):
        t = np.atleast_1d(np.asarray(t, float))
        cols = [t**k for k in range(n + 1)]
        cols += [np.where(t > uk, (t - uk)**n, 0.0) for uk in u[1:-1]]
        return np.column_stack(cols)
    c = np.linalg.lstsq(basis(x), np.asarray(y, float), rcond=None)[0]
    return lambda t: basis(t) @ c


def predict(y, m, n):
    """Линейное предсказание (метод Бёрга, порядок m) — n следующих значений."""
    y = np.asarray(y, float)
    f = y.copy(); b = y.copy(); a = np.array([1.0])
    for _ in range(m):
        ff, bb = f[1:], b[:-1]
        k = -2 * ff @ bb / (ff @ ff + bb @ bb)
        f, b = ff + k * bb, bb + k * ff
        a = np.concatenate([a, [0]]) + k * np.concatenate([a, [0]])[::-1]
    out = list(y)
    for _ in range(n):
        out.append(-np.dot(a[1:], out[::-1][:m]))
    return np.array(out[len(y):])


def line(x, y):
    a, b = np.polyfit(x, y, 1)
    return np.array([b, a])          # (intercept, slope)


def medfit(x, y):
    """Медиан-медианная прямая: три группы, наклон по медианам крайних групп."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    o = np.argsort(x); x, y = x[o], y[o]
    N = len(x)
    n1 = n3 = int(np.ceil(N / 3))     # крайние группы (как в Mathcad: 7 точек -> 3+1+3)
    L, M, R = slice(0, n1), slice(n1, N - n3), slice(N - n3, N)
    xl, yl = np.median(x[L]), np.median(y[L])
    xm, ym = np.median(x[M]), np.median(y[M])
    xr, yr = np.median(x[R]), np.median(y[R])
    a = (yr - yl) / (xr - xl)
    b = ((yl - a * xl) + (ym - a * xm) + (yr - a * xr)) / 3
    return np.array([b, a])


def regress(x, y, k):
    c = np.polyfit(x, y, k)
    return lambda t: np.polyval(c, t)


def loess(x, y, span):
    """Локальная квадратичная регрессия с весами tricube (доля точек span)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    q = max(3, int(np.floor(span * len(x))))

    def f(t):
        out = []
        for t0 in np.atleast_1d(t):
            d = np.abs(x - t0)
            h = np.sort(d)[min(q, len(x)) - 1]
            if span > 1:
                h *= span
            w = np.clip(1 - (d / h)**3, 0, None)**3
            X = np.column_stack([np.ones_like(x), x - t0, (x - t0)**2])
            W = np.sqrt(w)
            c = np.linalg.lstsq(X * W[:, None], y * W, rcond=None)[0]
            out.append(c[0])
        return np.array(out)
    return f


def expfit(x, y, g):
    return curve_fit(lambda t, a, b, c: a * np.exp(b * t) + c, x, y, p0=g, maxfev=20000)[0]


def linfit(x, y, F):
    A = np.column_stack([F(xi) for xi in x]).T
    return np.linalg.lstsq(A, y, rcond=None)[0]


def genfit(x, y, g, f):
    return curve_fit(f, x, y, p0=g, maxfev=20000)[0]


def medsmooth(y, b):
    """Бегущие медианы с окном b; на краях окно укорачивается симметрично."""
    y = np.asarray(y, float); n = len(y); h = (b - 1) // 2
    out = np.empty(n)
    for i in range(n):
        r = min(h, i, n - 1 - i)
        out[i] = np.median(y[i - r:i + r + 1])
    return out


def ksmooth(x, y, b):
    """Гауссово ядро; квартили ядра в точках ±0.25·b (как в Mathcad)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    s = 0.37 * b
    W = np.exp(-((x[:, None] - x[None, :]) / s)**2 / 2)
    return (W @ y) / W.sum(axis=1)


def _runsmooth(x, y, span):
    """Локальная линейная регрессия по span·n ближайшим соседям (для supsmooth)."""
    n = len(x); k = max(3, int(round(span * n)))
    out = np.empty(n); cv = np.empty(n)
    for i in range(n):
        lo = min(max(0, i - k // 2), n - k); idx = np.arange(lo, lo + k)
        c = np.polyfit(x[idx], y[idx], 1); out[i] = np.polyval(c, x[i])
        j = idx[idx != i]; c2 = np.polyfit(x[j], y[j], 1)
        cv[i] = abs(y[i] - np.polyval(c2, x[i]))
    return out, cv


def supsmooth(x, y):
    """Адаптивное сглаживание Фридмана: выбор окна из 0.05/0.2/0.5 по кросс-валидации."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    spans = [0.05, 0.2, 0.5]
    sm, cv = zip(*[_runsmooth(x, y, s) for s in spans])
    cvs = [_runsmooth(x, c, 0.2)[0] for c in cv]
    best = np.array(spans)[np.argmin(np.vstack(cvs), axis=0)]
    best_s = _runsmooth(x, best, 0.2)[0]
    res = np.array([np.interp(bs, spans, [s[i] for s in sm]) for i, bs in enumerate(best_s)])
    return _runsmooth(x, res, 0.05)[0]


def moving_average(y, w):
    """Формула рис. 3.19: среднее по w предыдущим точкам (в начале — по всем имеющимся)."""
    y = np.asarray(y, float)
    return np.array([y[:i + 1].mean() if i < w else y[i - w + 1:i + 1].mean() for i in range(len(y))])


def delta(y, fx):
    """Среднеквадратичное отклонение по формуле методички: sqrt(sum)/n."""
    y = np.asarray(y, float)
    return np.sqrt(np.sum((y - fx)**2)) / len(y)
