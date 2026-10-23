import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Исходные данные: фактическая производительность МАП-1, писем в час
y_o = np.array([17981, 18694, 19205, 18698, 18753, 18880,
                18661, 16844, 17707, 17535, 17972, 18584,
                16351, 17432, 17947, 17738, 16160, 15897], dtype=float)  # обычные дни
y_p = np.array([15942, 15429, 16339, 17853, 17894, 17329,
                17620, 16939, 15735, 17949, 16404, 15354], dtype=float)  # предпраздничные дни
n1, n2 = len(y_o), len(y_p)

# 3.1. Среднее арифметическое и среднее квадратическое отклонение
def characteristics(y):
    mean = np.sum(y) / len(y)
    s = np.sqrt(np.sum((y - mean) ** 2) / (len(y) - 1))
    return mean, s

mean_o, s_o = characteristics(y_o)
mean_p, s_p = characteristics(y_p)
print("3.1. Статистические характеристики")
print(f"Обычные дни:         n1 = {n1}, y_ср = {mean_o:.2f}, S = {s_o:.2f}")
print(f"Предпраздничные дни: n2 = {n2}, y_ср = {mean_p:.2f}, S = {s_p:.2f}")
print()

# 3.2. 95% доверительные интервалы для средних значений
t_o = stats.t.ppf(1 - 0.05 / 2, n1 - 1)   # 2,11
t_p = stats.t.ppf(1 - 0.05 / 2, n2 - 1)   # 2,20
d_o = t_o * s_o / np.sqrt(n1)
d_p = t_p * s_p / np.sqrt(n2)
ci_o = (mean_o - d_o, mean_o + d_o)
ci_p = (mean_p - d_p, mean_p + d_p)
print("3.2. 95% доверительные интервалы для средних")
print(f"t(0,975; {n1 - 1}) = {t_o:.3f}, t(0,975; {n2 - 1}) = {t_p:.3f}")
print(f"Обычные дни:         {mean_o:.1f} ± {d_o:.1f} -> [{ci_o[0]:.1f}; {ci_o[1]:.1f}]")
print(f"Предпраздничные дни: {mean_p:.1f} ± {d_p:.1f} -> [{ci_p[0]:.1f}; {ci_p[1]:.1f}]")
print()

# 3.3. Проверка пересечения интервалов
overlap = ci_p[1] - ci_o[0]
print("3.3. Пересечение доверительных интервалов")
if overlap > 0:
    print(f"Интервалы пересекаются, ширина пересечения {overlap:.1f} писем/ч")
else:
    print("Интервалы не пересекаются: различие значимо")
print()

# 3.3.2. 95% доверительный интервал для разности средних, формула (1)
t_d = stats.t.ppf(1 - 0.05 / 2, n1 + n2 - 2)   # 2,048
s_pool = np.sqrt(((n1 - 1) * s_o ** 2 + (n2 - 1) * s_p ** 2) / (n1 + n2 - 2))
diff = mean_o - mean_p
d_diff = t_d * np.sqrt((n1 + n2) / (n1 * n2)) * s_pool
ci_diff = (diff - d_diff, diff + d_diff)
print("3.3.2. Доверительный интервал для разности средних")
print(f"t(0,975; {n1 + n2 - 2}) = {t_d:.3f}, S_объед = {s_pool:.2f}")
print(f"{diff:.2f} ± {d_diff:.2f} -> [{ci_diff[0]:.1f}; {ci_diff[1]:.1f}]")
print("Интервал не содержит 0: различие значимо" if ci_diff[0] > 0 or ci_diff[1] < 0
      else "Интервал содержит 0: различие незначимо")
print()

# Проверка расчётным значением t-критерия Стьюдента
t_calc = diff / (s_pool * np.sqrt((n1 + n2) / (n1 * n2)))
print(f"Расчётный t = {t_calc:.3f}, табличный t = {t_d:.3f}")
print(f"Снижение производительности: {diff / mean_o * 100:.1f} %")

# График: исходные данные и доверительные интервалы
fig, ax = plt.subplots(figsize=(8, 6))
rng = np.random.default_rng(1)
ax.scatter(1 + rng.uniform(-0.08, 0.08, n1), y_o, color="tab:blue", alpha=0.6, label="Обычные дни")
ax.scatter(2 + rng.uniform(-0.08, 0.08, n2), y_p, color="tab:orange", alpha=0.6, label="Предпраздничные дни")
ax.errorbar([1.25], [mean_o], yerr=[[d_o], [d_o]], fmt="s", color="tab:blue", capsize=8, label="Среднее и 95% ДИ")
ax.errorbar([2.25], [mean_p], yerr=[[d_p], [d_p]], fmt="s", color="tab:orange", capsize=8)
ax.axhspan(ci_o[0], ci_p[1], color="grey", alpha=0.2, label="Пересечение интервалов")
ax.set_xticks([1, 2], ["Обычные дни", "Предпраздничные дни"])
ax.set_xlim(0.5, 2.6)
ax.set_ylabel("Производительность, писем/ч")
ax.set_title("Фактическая производительность АПСМ МАП-1")
ax.grid(True, alpha=0.4)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
plt.tight_layout()
plt.savefig("prak1_ci.png", dpi=200)
