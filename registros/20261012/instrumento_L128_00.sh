SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)" || exit 1
cd "$SCRIPT_DIR/../.." || exit 1
export TZ=UTC
python3 -B - <<'PY'
import math, numpy as np
C0=299792458.0; ETA0=376.730313668; MU0=ETA0/C0; EPS0=1.0/(ETA0*C0)
F0=10e9; LAM0=C0/F0; TAU=1.5/F0; TD=4.0*TAU; W=6*TAU
M=3; R0=1e-9; L_ESP=80e-3
EPS1=1.0; EPS2=4.0
Z1=ETA0/math.sqrt(EPS1); Z2=ETA0/math.sqrt(EPS2)
S11A=(Z2-Z1)/(Z2+Z1); S21A=2*math.sqrt(Z1*Z2)/(Z1+Z2)
T_TOTAL=8e-9

def perfil(n, dx):
    sig=np.zeros(n); smax=-(M+1)*math.log(R0)/(2.0*ETA0*L_ESP)
    N=int(round(L_ESP/dx))
    for i in range(N):
        f=(N-i)/float(N); sig[i]=smax*f**M; sig[n-1-i]=smax*f**M
    return sig, N

def corrida(dx, epsr, i_f, i_m1, i_m2, n_pasos, dt):
    n=epsr.size; eps=epsr*EPS0
    sig,_=perfil(n,dx)
    ca=(1.0-sig*dt/(2.0*eps))/(1.0+sig*dt/(2.0*eps))
    cb=(dt/(eps*dx))/(1.0+sig*dt/(2.0*eps)); ch=dt/(MU0*dx)
    ez=np.zeros(n); hy=np.zeros(n); m1=np.zeros(n_pasos); m2=np.zeros(n_pasos)
    for p in range(n_pasos):
        hy[:-1]-=ch*(ez[1:]-ez[:-1])
        ez[1:]=ca[1:]*ez[1:]-cb[1:]*(hy[1:]-hy[:-1])
        t=p*dt
        ez[i_f]+=-math.exp(-((t-TD)/TAU)**2)*math.sin(2*math.pi*F0*(t-TD))
        m1[p]=ez[i_m1]; m2[p]=ez[i_m2]
    return m1, m2

def dft(x, dt, f, t0, t1):
    n0=max(int(math.floor(t0/dt)),0); n1=min(int(math.ceil(t1/dt)), x.size)
    if n1<=n0: return 0j
    nn=np.arange(n0,n1,dtype=float)
    return complex(np.sum(x[n0:n1]*np.exp(-2j*math.pi*f*nn*dt))*dt)

print("UNIVERSO DECLARADO: Benchmark 1 TEM, eps1=1.0 eps2=4.0, f0=10 GHz, L_ESP=%.0f mm" % (L_ESP*1e3))
print("MOTOR: FDTD 1D Yee 1D, S_CFL=0.5, sigma_max=-(m+1)ln(R0)/(2 eta0 L_ESP)=%.6f S/m, m=%d, R0=%.0e" % (-(M+1)*math.log(R0)/(2*ETA0*L_ESP),M,R0))
print("UNIDAD: campo Ez transversal (V/m) en nodo. VENTANA: compuerta W=6 tau=%.0f ps en arribos geometricos" % (W*1e12))
print("ANALITICO: Z1=%.9f Z2=%.9f |S11|=%.12f |S21|=%.12f" % (Z1,Z2,abs(S11A),abs(S21A)))
print("")
print("dx(m)  celdas/l0  N_ABS  n  pasos   |S11|       e11%     |S21|       e21%     pot         cola_dB")
for dx in (1e-3, 5e-4, 2.5e-4):
    nlam=LAM0/dx
    _,N=perfil(1,dx)
    n=N
    i_f=N+int(round(15.0*nlam)); i_m1=N+int(round(16.5*nlam))
    i_esc=N+int(round(19.5*nlam)); i_m2=N+int(round(24.5*nlam))
    n=i_m2+int(round(10.0*nlam))+N+1
    dt=0.5*dx/C0; n_pasos=int(math.ceil(T_TOTAL/dt))
    v1=C0; v2=C0/math.sqrt(EPS2)
    t_inc=TD+(i_m1-i_f)*dx/v1
    t_ref=TD+(i_esc-i_f)*dx/v1+(i_esc-i_m1)*dx/v1
    t_tra=TD+(i_esc-i_f)*dx/v1+(i_m2-i_esc)*dx/v2
    ea=np.full(n,EPS1); eb=np.full(n,EPS1); eb[i_esc:]=EPS2
    m1a,_=corrida(dx,ea,i_f,i_m1,i_m2,n_pasos,dt)
    m1b,m2b=corrida(dx,eb,i_f,i_m1,i_m2,n_pasos,dt)
    ai=dft(m1a,dt,F0,t_inc-W/2,t_inc+W/2)
    ar=dft(m1b-m1a,dt,F0,t_ref-W/2,t_ref+W/2)
    at=dft(m2b,dt,F0,t_tra-W/2,t_tra+W/2)
    s11=ar/ai; s21=(at/ai)*math.sqrt(Z1/Z2)
    e11=abs(abs(s11)-abs(S11A))/abs(S11A); e21=abs(abs(s21)-abs(S21A))/abs(S21A)
    i0=int((t_inc+W/2)/dt)
    cola=np.max(np.abs(m1a[i0:])); p_inc=np.max(np.abs(m1a))
    print("%-.4g %6.0f %6d %5d %6d  %.8f  %6.4f  %.8f  %6.4f  %.8f  %7.2f" % (dx,nlam,N,n,n_pasos,abs(s11),100*e11,abs(s21),100*e21,abs(s11)**2+abs(s21)**2,20*math.log10(cola/p_inc)))
    eco=np.argmax(np.abs(m1a[i0:]))+i0
    print("      arribos geom: t_inc=%.0f t_ref=%.0f t_tra=%.0f / eco_esponja pico=%.0f / doble=%.0f ps" % (t_inc*1e12,t_ref*1e12,t_tra*1e12,eco*dt*1e12,(t_ref+2*(i_esc-i_m1)*dx/v1)*1e12))
PY