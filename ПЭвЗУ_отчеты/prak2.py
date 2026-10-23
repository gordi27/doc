import numpy as np
import matplotlib.pyplot as plt

# Исходные данные (табл. 1): время непрерывной работы МАП-1, ч,
# количество и интенсивность выгрузок писем из накопителей
t = np.array([1.812, 1.970, 2.082, 2.089, 2.253, 2.478, 2.540,
              3.041, 3.103, 3.584, 3.929, 4.839, 5.539])
B_b = np.array([60, 64, 59, 51, 90, 54, 73, 66, 72, 93, 91, 134, 119])
B_m = np.array([255, 250, 302, 296, 302, 311, 318, 349, 372, 392, 449, 467, 487])
lam_b = np.array([33.3, 32.5, 28.3, 24.4, 39.9, 21.8, 28.7, 21.7, 23.2, 26.0, 23.2, 27.7, 21.5])
lam_m = np.array([140.7, 126.9, 145.1, 141.7, 134.0, 126.7, 125.2, 114.8, 119.9, 109.4, 114.3, 96.5, 87.9])
N = len(t)
r_table = 0.476   # односторонний критерий, alpha = 0,05, f = N - 2 = 11


def correlation(t, lam):
    """Коэффициент корреляции по формуле (1)."""
    dt = t - t.mean()
    dl = lam - lam.mean()
    return np.sum(dt * dl) / np.sqrt(np.sum(dt ** 2) * np.sum(dl ** 2))


def least_squares(t, lam):
    """Коэффициенты b0, b1 уравнения lam = b0 + b1*t по формулам (2), (3)."""
    den = N * np.sum(t ** 2) - np.sum(t) ** 2
    b0 = (np.sum(lam) * np.sum(t ** 2) - np.sum(t) * np.sum(lam * t)) / den
    b1 = (N * np.sum(lam * t) - np.sum(lam) * np.sum(t)) / den
    return b0, b1


def calc_table(t, lam, name):
    """Расчётная таблица 2."""
    print(f"Таблица 2 ({name})")
    print(" i     t      λ     t-tср  (t-tср)^2  λ-λср  (λ-λср)^2  (t-tср)(λ-λср)    t^2      tλ")
    dt, dl = t - t.mean(), lam - lam.mean()
    for i in range(N):
        print(f"{i + 1:2d} {t[i]:6.3f} {lam[i]:6.1f} {dt[i]:7.3f} {dt[i] ** 2:8.3f} {dl[i]:7.2f} "
              f"{dl[i] ** 2:9.2f} {dt[i] * dl[i]:12.3f} {t[i] ** 2:9.3f} {t[i] * lam[i]:8.2f}")
    print(f" Σ {t.sum():6.3f} {lam.sum():6.1f} {abs(dt.sum()):7.3f} {np.sum(dt ** 2):8.3f} {abs(dl.sum()):7.2f} "
          f"{np.sum(dl ** 2):9.2f} {np.sum(dt * dl):12.3f} {np.sum(t ** 2):9.3f} {np.sum(t * lam):8.2f}")
    print()


results = {}
for name, lam in (("большой ёмкости", lam_b), ("малой ёмкости", lam_m)):
    calc_table(t, lam, name)
    r = correlation(t, lam)
    b0, b1 = least_squares(t, lam)
    results[name] = (r, b0, b1)
    print(f"Накопители {name}: r = {r:.3f}, |r| {'>' if abs(r) > r_table else '<='} r_табл = {r_table}")
    if r < 0 and abs(r) > r_table:
        print(f"Связь есть. Уравнение регрессии: λ = {b0:.2f} − {abs(b1):.3f}·t")
    else:
        print("Нуль-гипотеза не отклоняется: связь не установлена")
    print()

# Таблица 3: расчётные значения интенсивности и количества выгрузок
print("Таблица 3")
print(" t, ч   λб, 1/ч   λм, 1/ч    Вб     Вм")
for tt in range(2, 7):
    lb = results["большой ёмкости"][1] + results["большой ёмкости"][2] * tt
    lm = results["малой ёмкости"][1] + results["малой ёмкости"][2] * tt
    print(f"{tt:4d} {lb:9.1f} {lm:9.1f} {lb * tt:7.0f} {lm * tt:6.0f}")

# Графики: исходные точки и линии регрессии
tt = np.linspace(1.5, 6, 100)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for ax, (name, lam), color in zip(axes, (("большой ёмкости", lam_b), ("малой ёмкости", lam_m)),
                                  ("tab:blue", "tab:red")):
    r, b0, b1 = results[name]
    ax.scatter(t, lam, color=color, label="Опытные данные")
    ax.plot(tt, b0 + b1 * tt, color="black", label=f"λ = {b0:.2f} − {abs(b1):.3f}·t")
    ax.set_title(f"Накопители {name} (r = {r:.3f})")
    ax.set_xlabel("Время непрерывной работы t, ч")
    ax.set_ylabel("Интенсивность выгрузок λ, 1/ч")
    ax.grid(True, alpha=0.4)
    ax.legend()
plt.tight_layout()
plt.savefig("prak2_regr.png", dpi=200)
