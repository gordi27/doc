import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Вариант 4 (Приложение А)
x = np.round(np.arange(0, 1.2, 0.1), 1)
y = np.array([1.27, 2.25, 3.85, 4.45, 5.95, 6.12, 4.33, 3.78, 3.76, 2.53, 1.46, 1.19])
m1 = len(x)  # m + 1 = 12 узлов

# Суммы для нормальных систем (2.9), (2.11)
Sx = [np.sum(x**k) for k in range(5)]
Sxy = [np.sum(y * x**k) for k in range(3)]
for k in range(5):
    print(f"sum x^{k} = {Sx[k]:.6f}")
for k in range(3):
    print(f"sum x^{k}*y = {Sxy[k]:.6f}")

# Система (2.9): линейная регрессия
A1 = np.array([[Sx[0], Sx[1]], [Sx[1], Sx[2]]])
c_lin = np.linalg.solve(A1, Sxy[:2])
# Система (2.11): квадратичный многочлен
A2 = np.array([[Sx[i + j] for j in range(3)] for i in range(3)])
c_sq = np.linalg.solve(A2, Sxy)
print("phi1: c0, c1 =", c_lin)
print("phi2: c0, c1, c2 =", c_sq)

phi1 = c_lin[0] + c_lin[1] * x
phi2 = c_sq[0] + c_sq[1] * x + c_sq[2] * x**2
d1 = np.sqrt(np.sum((phi1 - y) ** 2))
d2 = np.sqrt(np.sum((phi2 - y) ** 2))
print(f"delta1 = {d1:.4f}, delta2 = {d2:.4f}")
for xi, yi, p1, p2 in zip(x, y, phi1, phi2):
    print(f"{xi:.1f} {yi:.2f} {p1:.4f} {p2:.4f} {(p1-yi)**2:.4f} {(p2-yi)**2:.4f}")

t = np.linspace(0, 1.1, 200)
plt.figure(figsize=(7, 4.5))
plt.plot(x, y, "ko", label="y(x) — исходные данные")
plt.plot(t, c_lin[0] + c_lin[1] * t, "b-", label="φ1(x) — линейная регрессия")
plt.plot(t, c_sq[0] + c_sq[1] * t + c_sq[2] * t**2, "r-", label="φ2(x) — квадратичный многочлен")
plt.xlabel("x"); plt.ylabel("y"); plt.grid(True, alpha=0.4); plt.legend()
plt.tight_layout(); plt.savefig("lab2_plot.png", dpi=200)
