// ЛР2, вариант 4. Выполнять после моделирования lab2_pd.zcos и lab2_pid.zcos
// (блоки TOWS_c создают в рабочем пространстве переменные phi и delta)
// --- после моделирования lab2_tows.zcos (ПД, без возмущения, 100 с):
// scf(); subplot(2,1,1); plot(phi.time, phi.values); title('Курс'); xlabel('Время, сек'); ylabel('$\phi, градусы$');
// subplot(2,1,2); plot(delta.time, delta.values); title('Угол поворота руля'); xlabel('Время, сек'); ylabel('$\delta, градусы$');
// --- после моделирования lab2_pd.zcos (ПД + возмущение, 500 с):
// phi0 = phi; delta0 = delta;
// --- затем моделирование lab2_pid.zcos (ПИД + возмущение, 500 с)
K = 0.07; Ts = 16.6;
P = syslin('c', K, Ts*%s^2+%s)
TR = 2; Toc = 4;
R = syslin('c', 1, TR*%s+1)
H = syslin('c', 1, Toc*%s+1)
C0 = syslin('c', 13.53*%s+0.7, %s+1)
Wf0 = P/.(R*C0*H)
kf0 = horner(Wf0, 0)
phiSt0 = 10 + kf0*2
C = C0 + syslin('c', 1, 200*%s)
Wf = P/.(R*C*H)
kf = horner(Wf, 0)
phiSt = 10 + kf*2
// scf(); subplot(2,1,1); plot(phi0.time, phi0.values, phi.time, phi.values); title('Курс');
// xlabel('Время, сек'); ylabel('$\phi, градусы$'); legend('ПД-регулятор', 'ПИД-регулятор');
// subplot(2,1,2); plot(delta0.time, delta0.values, delta.time, delta.values); title('Угол поворота руля');
// xlabel('Время, сек'); ylabel('$\delta, градусы$'); legend('ПД-регулятор', 'ПИД-регулятор');
Wopen = C*R*P*H
Gm_dB = g_margin(Wopen)
Pm = p_margin(Wopen)
