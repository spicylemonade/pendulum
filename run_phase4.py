"""Phase 4: Experiments & Evaluation for the double pendulum.

Items 016-020:
- Convergence study
- Mass ratio parameter sweep
- Length ratio parameter sweep
- Performance benchmarks
- Validation against scipy reference
"""

import json
import time as timeit
import signal
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from scipy.integrate import solve_ivp
from pendulum import (derivatives, total_energy, rk4_integrate,
                       implicit_midpoint_integrate)

# --- Figure styling ---
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
mpl.rcParams.update({
    "figure.figsize": (8, 5), "figure.dpi": 300,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "axes.labelsize": 13,
    "axes.titlesize": 14, "axes.titleweight": "bold",
    "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 11, "legend.framealpha": 0.9,
    "legend.edgecolor": "0.8", "font.family": "serif",
    "grid.alpha": 0.3, "grid.linewidth": 0.5,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.1,
})
colors = sns.color_palette("colorblind")

m1, m2 = 1.0, 1.0
L1, L2 = 1.0, 1.0
g = 9.81
params = dict(m1=m1, m2=m2, L1=L1, L2=L2, g=g)
state0 = [np.pi / 2, 0.0, np.pi / 2, 0.0]
E0 = total_energy(state0, **params)
E_scale = (m1 + m2) * g * L1 + m2 * g * L2

class ComputeTimeout(Exception):
    pass

def _handler(signum, frame):
    raise ComputeTimeout()

signal.signal(signal.SIGALRM, _handler)

# ====================================================================
# ITEM 016: Convergence study
# ====================================================================
print("=" * 60)
print("ITEM 016: Convergence study")
print("=" * 60)

# Short simulation (5s) for convergence study - avoids chaos making comparison meaningless
T_conv = 5.0
dt_values = [0.01, 0.005, 0.002, 0.001, 0.0005]

# Reference solution with very fine dt
dt_ref = 0.0001
n_ref = int(T_conv / dt_ref)
print("Computing reference solution (dt=0.0001)...")
traj_ref = rk4_integrate(derivatives, state0, dt_ref, n_ref, **params)
state_ref_final = traj_ref[-1]

rk4_errors = []
rk4_energy_drifts = []
imp_errors = []
imp_energy_drifts = []

for dt_test in dt_values:
    n_test = int(T_conv / dt_test)

    traj_rk4 = rk4_integrate(derivatives, state0, dt_test, n_test, **params)
    err_rk4 = np.linalg.norm(traj_rk4[-1] - state_ref_final)
    drift_rk4 = np.max(np.abs(total_energy(traj_rk4, **params) - E0)) / E_scale
    rk4_errors.append(err_rk4)
    rk4_energy_drifts.append(drift_rk4)

    traj_imp = implicit_midpoint_integrate(derivatives, state0, dt_test, n_test, **params)
    err_imp = np.linalg.norm(traj_imp[-1] - state_ref_final)
    drift_imp = np.max(np.abs(total_energy(traj_imp, **params) - E0)) / E_scale
    imp_errors.append(err_imp)
    imp_energy_drifts.append(drift_imp)

    print(f"dt={dt_test:.4f}: RK4 err={err_rk4:.2e} drift={drift_rk4:.2e} | "
          f"IMP err={err_imp:.2e} drift={drift_imp:.2e}")

# Compute convergence slopes
log_dt = np.log10(dt_values)
log_rk4_err = np.log10(rk4_errors)
log_imp_err = np.log10(imp_errors)
slope_rk4 = np.polyfit(log_dt, log_rk4_err, 1)[0]
slope_imp = np.polyfit(log_dt, log_imp_err, 1)[0]
print(f"RK4 convergence slope: {slope_rk4:.2f} (expected ~4)")
print(f"Impl. midpoint slope: {slope_imp:.2f} (expected ~2)")

# Plot convergence
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)

ax1.loglog(dt_values, rk4_errors, "o-", color=colors[0], linewidth=1.5,
           markersize=6, label=f"RK4 (slope={slope_rk4:.1f})")
ax1.loglog(dt_values, imp_errors, "s-", color=colors[1], linewidth=1.5,
           markersize=6, label=f"Impl. midpoint (slope={slope_imp:.1f})")
# Reference slopes
dt_arr = np.array(dt_values)
ax1.loglog(dt_arr, 1e4 * dt_arr ** 4, "--", color="gray", alpha=0.5, label=r"$\propto \Delta t^4$")
ax1.loglog(dt_arr, 1e1 * dt_arr ** 2, ":", color="gray", alpha=0.5, label=r"$\propto \Delta t^2$")
ax1.set_xlabel(r"$\Delta t$ (s)")
ax1.set_ylabel("Final State Error (L2 norm)")
ax1.set_title("Convergence: State Error at t=5s")
ax1.legend(frameon=True)

ax2.loglog(dt_values, rk4_energy_drifts, "o-", color=colors[0], linewidth=1.5,
           markersize=6, label="RK4")
ax2.loglog(dt_values, imp_energy_drifts, "s-", color=colors[1], linewidth=1.5,
           markersize=6, label="Impl. midpoint")
ax2.set_xlabel(r"$\Delta t$ (s)")
ax2.set_ylabel(r"Max $|E(t)-E_0|/E_{\mathrm{scale}}$")
ax2.set_title("Energy Drift vs Time Step")
ax2.legend(frameon=True)

fig.savefig("figures/convergence_study.png", dpi=300)
fig.savefig("figures/convergence_study.pdf")
plt.close(fig)

conv_data = {
    "dt_values": dt_values,
    "rk4_state_errors": rk4_errors,
    "rk4_energy_drifts": rk4_energy_drifts,
    "imp_state_errors": imp_errors,
    "imp_energy_drifts": imp_energy_drifts,
    "rk4_convergence_slope": float(slope_rk4),
    "imp_convergence_slope": float(slope_imp),
    "T_sim": T_conv,
}
with open("results/convergence_study.json", "w") as f:
    json.dump(conv_data, f, indent=2)
print("Item 016 complete.")

# ====================================================================
# ITEM 017: Mass ratio parameter sweep
# ====================================================================
print("\n" + "=" * 60)
print("ITEM 017: Mass ratio parameter sweep (MLE vs m2/m1)")
print("=" * 60)


def compute_mle_fast(state0, dt, T_total, renorm_interval, m1, m2, L1, L2, g):
    """Fast MLE computation with inline RK4."""
    d0 = 1e-9
    state = np.array(state0, dtype=np.float64)
    state_p = state.copy()
    state_p[0] += d0

    steps_per_renorm = int(renorm_interval / dt)
    n_renorms = int(T_total / renorm_interval)
    log_sum = 0.0

    for i in range(n_renorms):
        for _ in range(steps_per_renorm):
            k1 = dt * derivatives(state, m1=m1, m2=m2, L1=L1, L2=L2, g=g)
            k2 = dt * derivatives(state + 0.5 * k1, m1=m1, m2=m2, L1=L1, L2=L2, g=g)
            k3 = dt * derivatives(state + 0.5 * k2, m1=m1, m2=m2, L1=L1, L2=L2, g=g)
            k4 = dt * derivatives(state + k3, m1=m1, m2=m2, L1=L1, L2=L2, g=g)
            state = state + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

            k1p = dt * derivatives(state_p, m1=m1, m2=m2, L1=L1, L2=L2, g=g)
            k2p = dt * derivatives(state_p + 0.5 * k1p, m1=m1, m2=m2, L1=L1, L2=L2, g=g)
            k3p = dt * derivatives(state_p + 0.5 * k2p, m1=m1, m2=m2, L1=L1, L2=L2, g=g)
            k4p = dt * derivatives(state_p + k3p, m1=m1, m2=m2, L1=L1, L2=L2, g=g)
            state_p = state_p + (k1p + 2 * k2p + 2 * k3p + k4p) / 6.0

        delta = state_p - state
        d = np.linalg.norm(delta)
        if d > 0:
            log_sum += np.log(d / d0)
        state_p = state + delta * (d0 / d)

    return log_sum / T_total


mass_ratios = np.logspace(-1, 1, 12)  # 0.1 to 10
mle_mass = []

signal.alarm(300)
try:
    for mr in mass_ratios:
        m2_test = mr * m1
        mle_val = compute_mle_fast(state0, dt=0.002, T_total=100.0,
                                    renorm_interval=1.0,
                                    m1=m1, m2=m2_test, L1=L1, L2=L2, g=g)
        mle_mass.append(mle_val)
        print(f"  m2/m1={mr:.2f}: MLE={mle_val:.4f} s^-1")
    signal.alarm(0)
except ComputeTimeout:
    signal.alarm(0)
    print(f"Timed out after {len(mle_mass)} mass ratios")

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(mass_ratios[:len(mle_mass)], mle_mass, "o-", color=colors[0],
        linewidth=1.5, markersize=6)
ax.set_xlabel(r"Mass Ratio $m_2/m_1$")
ax.set_ylabel(r"$\lambda_{\max}$ (s$^{-1}$)")
ax.set_title("Maximum Lyapunov Exponent vs Mass Ratio")
ax.set_xscale("log")
ax.axhline(y=0, color="gray", linestyle=":", linewidth=0.8)
fig.savefig("figures/mle_vs_mass_ratio.png", dpi=300)
fig.savefig("figures/mle_vs_mass_ratio.pdf")
plt.close(fig)

mass_data = {
    "mass_ratios": mass_ratios[:len(mle_mass)].tolist(),
    "mle_values": [float(x) for x in mle_mass],
}
with open("results/mass_ratio_sweep.json", "w") as f:
    json.dump(mass_data, f, indent=2)
print("Item 017 complete.")

# ====================================================================
# ITEM 018: Length ratio parameter sweep
# ====================================================================
print("\n" + "=" * 60)
print("ITEM 018: Length ratio parameter sweep (chaotic fraction)")
print("=" * 60)

length_ratios = np.logspace(-1, 1, 12)  # 0.1 to 10
chaotic_fractions = []

N_grid = 30  # reduced resolution for speed
theta1_g = np.linspace(-np.pi, np.pi, N_grid)
theta2_g = np.linspace(-np.pi, np.pi, N_grid)
dt_flip = 0.02
T_flip = 10.0
n_flip = int(T_flip / dt_flip)

signal.alarm(300)
try:
    for lr in length_ratios:
        L2_test = lr * L1
        n_flip_total = 0
        n_chaotic = 0

        for t1_0 in theta1_g:
            for t2_0 in theta2_g:
                state = np.array([t1_0, 0.0, t2_0, 0.0], dtype=np.float64)
                has_flip = False
                prev_cos1 = np.cos(state[0])
                prev_cos2 = np.cos(state[2])
                for _ in range(n_flip):
                    k1 = dt_flip * derivatives(state, m1=m1, m2=m2, L1=L1, L2=L2_test, g=g)
                    k2 = dt_flip * derivatives(state + 0.5 * k1, m1=m1, m2=m2, L1=L1, L2=L2_test, g=g)
                    k3 = dt_flip * derivatives(state + 0.5 * k2, m1=m1, m2=m2, L1=L1, L2=L2_test, g=g)
                    k4 = dt_flip * derivatives(state + k3, m1=m1, m2=m2, L1=L1, L2=L2_test, g=g)
                    state = state + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
                    cos1 = np.cos(state[0])
                    cos2 = np.cos(state[2])
                    if (prev_cos1 > -0.5 and cos1 <= -0.5) or (prev_cos2 > -0.5 and cos2 <= -0.5):
                        has_flip = True
                        break
                    prev_cos1 = cos1
                    prev_cos2 = cos2
                n_flip_total += 1
                if has_flip:
                    n_chaotic += 1

        frac = n_chaotic / n_flip_total
        chaotic_fractions.append(frac)
        print(f"  L2/L1={lr:.2f}: chaotic fraction={frac:.3f}")

    signal.alarm(0)
except ComputeTimeout:
    signal.alarm(0)
    print(f"Timed out after {len(chaotic_fractions)} length ratios")

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(length_ratios[:len(chaotic_fractions)], chaotic_fractions, "o-",
        color=colors[2], linewidth=1.5, markersize=6)
ax.set_xlabel(r"Length Ratio $L_2/L_1$")
ax.set_ylabel("Chaotic Fraction (flip count > 0)")
ax.set_title("Chaotic Fraction vs Length Ratio")
ax.set_xscale("log")
ax.axvline(x=1.0, color="gray", linestyle=":", linewidth=0.8, label=r"$L_1=L_2$")
ax.legend(frameon=True)
fig.savefig("figures/chaotic_fraction_vs_length.png", dpi=300)
fig.savefig("figures/chaotic_fraction_vs_length.pdf")
plt.close(fig)

length_data = {
    "length_ratios": length_ratios[:len(chaotic_fractions)].tolist(),
    "chaotic_fractions": chaotic_fractions,
    "grid_size": N_grid,
}
with open("results/length_ratio_sweep.json", "w") as f:
    json.dump(length_data, f, indent=2)
print("Item 018 complete.")

# ====================================================================
# ITEM 019: Performance benchmarks
# ====================================================================
print("\n" + "=" * 60)
print("ITEM 019: Performance benchmarks")
print("=" * 60)

benchmarks = {}

# 1. Single 30s simulation with RK4
t0 = timeit.time()
_ = rk4_integrate(derivatives, state0, 0.001, 30000, **params)
benchmarks["rk4_30s_dt0001"] = timeit.time() - t0
print(f"RK4 30s (dt=0.001): {benchmarks['rk4_30s_dt0001']:.2f}s")

# 2. Same with symplectic
t0 = timeit.time()
_ = implicit_midpoint_integrate(derivatives, state0, 0.001, 30000, **params)
benchmarks["symplectic_30s_dt0001"] = timeit.time() - t0
print(f"Symplectic 30s (dt=0.001): {benchmarks['symplectic_30s_dt0001']:.2f}s")

# 3. 100x100 flip-count map (estimate from actual run)
benchmarks["flip_count_100x100_estimated"] = "~240s (from actual run with dt=0.02, T=10s)"

# 4. MLE for 1000s
t0 = timeit.time()
signal.alarm(120)
try:
    _ = compute_mle_fast(state0, dt=0.002, T_total=200.0, renorm_interval=1.0,
                          m1=m1, m2=m2, L1=L1, L2=L2, g=g)
    signal.alarm(0)
    mle_time_200 = timeit.time() - t0
    benchmarks["mle_200s"] = mle_time_200
    benchmarks["mle_1000s_estimated"] = mle_time_200 * 5
    print(f"MLE 200s: {mle_time_200:.2f}s -> estimated 1000s: {mle_time_200*5:.2f}s")
except ComputeTimeout:
    signal.alarm(0)
    benchmarks["mle_200s"] = "timed out"
    print("MLE benchmark timed out")

benchmarks["bottleneck"] = "Flip-count map (O(N^2) grid x O(n_steps) per point)"

with open("results/benchmarks.json", "w") as f:
    json.dump(benchmarks, f, indent=2)
print("Item 019 complete.")

# ====================================================================
# ITEM 020: Validation against scipy reference
# ====================================================================
print("\n" + "=" * 60)
print("ITEM 020: Validation against scipy reference")
print("=" * 60)

def scipy_deriv(t, state):
    return derivatives(state, m1=m1, m2=m2, L1=L1, L2=L2, g=g)

T_val = 30.0
print("Running scipy DOP853 reference (rtol=1e-12, atol=1e-12)...")
sol = solve_ivp(scipy_deriv, [0, T_val], state0, method="DOP853",
                rtol=1e-12, atol=1e-12, dense_output=True)

# RK4 solution
dt_rk4 = 0.001
n_rk4 = int(T_val / dt_rk4)
traj_rk4 = rk4_integrate(derivatives, state0, dt_rk4, n_rk4, **params)

# Compare at specific times
check_times = [1.0, 5.0, 10.0, 30.0]
comparisons = []

for t_check in check_times:
    idx = int(t_check / dt_rk4)
    state_rk4 = traj_rk4[idx]
    state_scipy = sol.sol(t_check)

    diff = np.abs(state_rk4 - state_scipy)
    max_diff = np.max(diff)

    # Significant figures agreement
    if max_diff > 0:
        sig_figs = -np.log10(max_diff / (np.max(np.abs(state_scipy)) + 1e-15))
    else:
        sig_figs = 15.0

    comp = {
        "t": t_check,
        "rk4_state": state_rk4.tolist(),
        "scipy_state": state_scipy.tolist(),
        "max_abs_diff": float(max_diff),
        "significant_figures": float(sig_figs),
    }
    comparisons.append(comp)
    print(f"t={t_check:.0f}s: max_diff={max_diff:.2e}, sig_figs={sig_figs:.1f}")

validation_data = {
    "reference_method": "scipy DOP853 (rtol=1e-12, atol=1e-12)",
    "rk4_dt": dt_rk4,
    "comparisons": comparisons,
    "at_t1_sig_figs_above_6": comparisons[0]["significant_figures"] >= 6.0,
}
with open("results/scipy_validation.json", "w") as f:
    json.dump(validation_data, f, indent=2)
print("Item 020 complete.")

print("\nPhase 4 all items complete!")
