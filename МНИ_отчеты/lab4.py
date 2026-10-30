import numpy as np

# План ПФЭ 2^4 в порядке табл. 4.2
N, k, m = 16, 4, 5
X = np.array([[1] + [1 if (u >> i) % 2 == 0 else -1 for i in range(k)] for u in range(N)])

# Проверка свойств плана (4.5)–(4.7)
orth = {(i, j): int(X[:, i] @ X[:, j]) for i in range(k + 1) for j in range(i + 1, k + 1)}
sym = [int(X[:, i].sum()) for i in range(1, k + 1)]
norm = [int((X[:, i] ** 2).sum()) for i in range(1, k + 1)]
print("ортогональность:", orth)
print("симметричность:", sym, " нормировка:", norm)

# Результаты наблюдений (m = 5 повторений в каждом опыте), влажность материала, %
rng = np.random.default_rng(11)
true = 17 - 6 * X[:, 1] + 1.5 * X[:, 2] - 1.0 * X[:, 3] + 1.0 * X[:, 4]
Y = np.round(true[:, None] + rng.normal(0, 1.1, (N, m))).astype(float)

t = 2.78  # критерий Стьюдента, P = 0,95, m = 5 (Приложение Б)

def mean_var(row):
    v = row[~np.isnan(row)]
    return v.mean(), v.var(ddof=1)

# Табл. 4.3: среднее (4.8) и дисперсия (4.9); доверительный интервал (4.10)
Y2 = Y.copy()
print("\nТабл. 4.3")
for u in range(N):
    Yu, S2 = mean_var(Y[u])
    d = t * np.sqrt(S2) / np.sqrt(m)
    out = [i for i in range(m) if not (Yu - d <= Y[u, i] <= Yu + d)]
    Y2[u, out] = np.nan
    print(u + 1, Y[u].astype(int), f"Yu={Yu:.2f} S2={S2:.3f} int=[{Yu - d:.2f}; {Yu + d:.2f}] промахи={[i + 1 for i in out]}")

# Табл. 4.4: пересчёт после исключения промахов
print("\nТабл. 4.4")
S2 = np.array([mean_var(r)[1] for r in Y2]); Ym = np.array([mean_var(r)[0] for r in Y2])
for u in range(N):
    print(u + 1, Y2[u], f"Yu={Ym[u]:.2f} S2={S2[u]:.3f}")

# Однородность дисперсий: Кохрен (4.11), Фишер (4.12); дисперсия воспроизводимости (4.13)
G = S2.max() / S2.sum(); F = S2.max() / S2.min(); Sy2 = S2.sum() / N
print(f"\nsum S2 = {S2.sum():.3f}, S2max = {S2.max():.3f}, S2min = {S2.min():.3f}")
print(f"G = {G:.3f} (Gт = 0,242), F = {F:.2f} (Fт = 6,39), Sy2 = {Sy2:.3f}")
