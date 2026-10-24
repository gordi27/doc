// ЛР1, вариант 4
clear
clc
n = poly([0.091 1.04 1.3],'s','coeff')
d = poly([0.9091 2.0264 2.1909 1],'s','coeff')
f = syslin('c', n, d)
n1 = f.num   // в Scilab 2024 вместо numer(f)
d1 = f.den   // вместо denom(f)
z = roots(n)
p = roots(d)
k = horner(f, 0)
f_ss = tf2ss(f)
f_ss.D = 1;
k1 = horner(ss2tf(f_ss), 0)
%e
%pi
scf(0); plzr(f);
[wc,ksi,pp] = damp(f)
t = [0:0.05:30];
yImp = csim('impuls', t, f);
yImp2 = csim('impuls', t, f_ss);
scf(1); plot(t, yImp, 'b-'); plot(t, yImp2, 'r-'); xgrid();
legend(['f','f_ss']); xlabel('t, c'); ylabel('w(t)');
yStep = csim('step', t, f);
yInf = k
ovr = max(yStep-yInf)/yInf*100
err = abs(yStep-yInf);
ind = find(err >= 0.05*yInf);
set_time = t(max(ind)+1)
yStep2 = csim('step', t, f_ss);
yInf2 = k1
max1 = max(yStep)
max2 = max(yStep2)
ovr2 = max(yStep2-yInf2)/yInf2*100
err2 = abs(yStep2-yInf2);
ind2 = find(err2 >= 0.05*yInf2);
set_time2 = t(max(ind2)+1)
scf(2); plot(t, yStep, 'b-'); plot(t, yStep2, 'r-'); xgrid();
legend(['f','f_ss'],1); xlabel('t, c'); ylabel('h(t)');
w = logspace(-2, 2, 100);
fResp = repfreq(f, w/(2*%pi));
Aw = abs(fResp);
scf(3); plot2d("ln", w, Aw); xgrid(); xlabel('w, рад/с'); ylabel('A(w)');
M = max(Aw) / Aw(1)
Aw1 = Aw(1)
k3dB = 10^(-3/20);
ind = find(Aw > k3dB*Aw(1));
B = max( w(ind) )
xs2png(0,'plzr.png'); xs2png(1,'imp.png'); xs2png(2,'step.png'); xs2png(3,'ach.png');
