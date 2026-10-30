"""Аналог CurveFinder из CurveExpert 1.4: подбор моделей и ранжирование по стандартной ошибке S."""
import numpy as np
from scipy.optimize import curve_fit

E = np.exp
MODELS = {  # имя CurveExpert: (формула, функция, начальные значения)
    'Linear Fit': ('y = a + bx', lambda x, a, b: a + b*x, [1, 1]),
    'Quadratic Fit': ('y = a + bx + cx²', lambda x, a, b, c: a + b*x + c*x**2, [1, 1, 1]),
    'Exponential Fit': ('y = a·e^(bx)', lambda x, a, b: a*E(b*x), [1, 0.1]),
    'Modified Power': ('y = a·b^x', lambda x, a, b: a*np.abs(b)**x, [1, 1.1]),
    'Exponential Association (2)': ('y = a(1 − e^(−bx))', lambda x, a, b: a*(1 - E(-b*x)), [5, 1]),
    'Exponential Association (3)': ('y = a(b − e^(−cx))', lambda x, a, b, c: a*(b - E(-c*x)), [5, 1, 1]),
    'Saturation-Growth Rate': ('y = ax/(b + x)', lambda x, a, b: a*x/(b + x), [5, 1]),
    'Reciprocal Model': ('y = 1/(a + bx)', lambda x, a, b: 1/(a + b*x), [1, 0.1]),
    'Reciprocal Quadratic': ('y = 1/(a + bx + cx²)', lambda x, a, b, c: 1/(a + b*x + c*x**2), [0.5, -1, 1]),
    'Logistic Model': ('y = a/(1 + b·e^(−cx))', lambda x, a, b, c: a/(1 + b*E(-c*x)), [5, 1, 1]),
    'Gompertz Relation': ('y = a·e^(−e^(b − cx))', lambda x, a, b, c: a*E(-E(b - c*x)), [5, 1, 1]),
    'Bleasdale Model': ('y = (a + bx)^(−1/c)', lambda x, a, b, c: np.abs(a + b*x)**(-1/c), [1, 1, 1]),
    'Sinusoidal Fit': ('y = a + b·cos(cx + d)', lambda x, a, b, c, d: a + b*np.cos(c*x + d), [3, 2, 5, -2.5]),
    'Gaussian Model': ('y = a·e^(−(x − b)²/(2c²))', lambda x, a, b, c: a*E(-(x - b)**2/(2*c**2)), [6, 0.5, 0.3]),
    'Rational Function': ('y = (a + bx)/(1 + cx + dx²)', lambda x, a, b, c, d: (a + b*x)/(1 + c*x + d*x**2), [1, 1, -1, 1]),
    'Heat Capacity': ('y = a + bx + c/x²', None, None),        # не определены при x = 0
    'Hyperbolic Fit': ('y = a + b/x', None, None),
    'Logarithm Fit': ('y = a + b·ln x', None, None),
    'Power Fit': ('y = a·x^b', None, None),
}


def stats(y, yf, p):
    n = len(y)
    S = np.sqrt(np.sum((y - yf)**2) / (n - p))                       # стандартная ошибка
    r = np.sqrt(max(0, 1 - np.sum((y - yf)**2) / np.sum((y - y.mean())**2)))  # коэф. корреляции
    return S, r


def curvefinder(x, y, poly_order):
    res = []
    for name, (formula, f, p0) in MODELS.items():
        if f is None:
            continue
        try:
            with np.errstate(all='ignore'):
                c, _ = curve_fit(f, x, y, p0=p0, maxfev=50000)
                yf = f(x, *c)
            if not np.all(np.isfinite(yf)):
                continue
            S, r = stats(y, yf, len(c))
            res.append((name, formula, c, S, r, f))
        except Exception:
            pass
    c = np.polyfit(x, y, poly_order)
    S, r = stats(y, np.polyval(c, x), poly_order + 1)
    res.append(('Polynomial Fit', f'полином {poly_order}-й степени', c[::-1], S, r,
                lambda t, *cc: np.polyval(cc[::-1], t)))
    return sorted(res, key=lambda q: q[3])


def lagrange(x, y):
    """Коэффициенты интерполяционного полинома Лагранжа (степень n−1) по возрастанию степеней."""
    c = np.zeros(len(x))
    for i in range(len(x)):
        p = np.poly1d([1.0])
        for j in range(len(x)):
            if j != i:
                p *= np.poly1d([1, -x[j]]) / (x[i] - x[j])
        c += y[i] * p.coeffs[::-1]
    return c
