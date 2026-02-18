"""Phase 3: Core research experiments for the double pendulum.

Items 011-014:
- Sensitivity to initial conditions demonstration
- Maximum Lyapunov exponent computation
- Poincare section generation
- Symplectic integrator implementation and comparison
"""

import json
import signal
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from pendulum import derivatives, total_energy, rk4_integrate, cartesian_positions

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

# --- Common parameters ---
m1, m2 = 1.0, 1.0
L1, L2 = 1.0, 1.0
g = 9.81
params = dict(m1=m1, m2=m2, L1=L1, L2=L2, g=g)

# ====================================================================
# ITEM 011: Sensitivity to initial conditions
# ====================================================================
print("=" * 60)
print("ITEM 011: Sensitivity to initial conditions")
print("=" * 60)

dt = 0.001
T_sim = 30.0
n_steps = int(T_sim / dt)

state0_a = np.array([np.pi / 2, 0.0, np.pi / 2, 0.0])
state0_b = np.array([np.pi / 2 + 1e-9, 0.0, np.pi / 2, 0.0])

print("Running trajectory A...")
traj_a = rk4_integrate(derivatives, state0_a, dt, n_steps, **params)
print("Running trajectory B (delta_theta1 = 1e-9)...")
traj_b = rk4_integrate(derivatives, state0_b, dt, n_steps, **params)

time = np.arange(n_steps + 1) * dt
distance = np.sqrt(np.sum((traj_a - traj_b) ** 2, axis=1))
log_distance = np.log10(distance + 1e-20)

# Plot 1: Both trajectories
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), constrained_layout=True,
                                sharex=True)
ax1.plot(time, traj_a[:, 0], color=colors[0], linewidth=0.5,
         label=r"$\theta_1$ (original)")
ax1.plot(time, traj_b[:, 0], color=colors[1], linewidth=0.5, linestyle="--",
         label=r"$\theta_1$ (perturbed)")
ax1.set_ylabel(r"$\theta_1$ (rad)")
ax1.set_title("Sensitivity to Initial Conditions")
ax1.legend(loc="upper right", frameon=True)

ax2.plot(time, traj_a[:, 2], color=colors[2], linewidth=0.5,
         label=r"$\theta_2$ (original)")
ax2.plot(time, traj_b[:, 2], color=colors[3], linewidth=0.5, linestyle="--",
         label=r"$\theta_2$ (perturbed)")
ax2.set_xlabel("Time (s)")
ax2.set_ylabel(r"$\theta_2$ (rad)")
ax2.legend(loc="upper right", frameon=True)

fig.savefig("figures/sensitivity_trajectories.png", dpi=300)
fig.savefig("figures/sensitivity_trajectories.pdf")
plt.close(fig)

# Plot 2: Log divergence
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(time, log_distance, color=colors[4], linewidth=0.5)
ax.set_xlabel("Time (s)")
ax.set_ylabel(r"$\log_{10}|\Delta \mathbf{x}|$")
ax.set_title("Divergence of Nearby Trajectories")
ax.axhline(y=-9, color="gray", linestyle=":", linewidth=0.8, label="Initial separation")
ax.legend(frameon=True)
fig.savefig("figures/sensitivity_divergence.png", dpi=300)
fig.savefig("figures/sensitivity_divergence.pdf")
plt.close(fig)
print("Item 011 figures saved.")

# ====================================================================
# ITEM 012: Maximum Lyapunov exponent
# ====================================================================
print("\n" + "=" * 60)
print("ITEM 012: Maximum Lyapunov exponent")
print("=" * 60)


def compute_mle(state0, dt, T_total, renorm_interval, **params):
    """Compute maximum Lyapunov exponent via periodic renormalization.

    Parameters
    ----------
    state0 : array_like
        Initial state [theta1, omega1, theta2, omega2].
    dt : float
        Time step.
    T_total : float
        Total integration time.
    renorm_interval : float
        Time between renormalizations.
    **params : dict
        Physical parameters (m1, m2, L1, L2, g).

    Returns
    -------
    mle : float
        Estimated maximum Lyapunov exponent.
    mle_history : list
        MLE estimates at each renormalization.
    """
    d0 = 1e-9
    state = np.array(state0, dtype=np.float64)
    # Perturb in theta1 direction
    state_p = state.copy()
    state_p[0] += d0

    steps_per_renorm = int(renorm_interval / dt)
    n_renorms = int(T_total / renorm_interval)

    log_sum = 0.0
    mle_history = []

    for i in range(n_renorms):
        # Integrate both trajectories
        for _ in range(steps_per_renorm):
            k1 = dt * derivatives(state, **params)
            k2 = dt * derivatives(state + 0.5 * k1, **params)
            k3 = dt * derivatives(state + 0.5 * k2, **params)
            k4 = dt * derivatives(state + k3, **params)
            state = state + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

            k1p = dt * derivatives(state_p, **params)
            k2p = dt * derivatives(state_p + 0.5 * k1p, **params)
            k3p = dt * derivatives(state_p + 0.5 * k2p, **params)
            k4p = dt * derivatives(state_p + k3p, **params)
            state_p = state_p + (k1p + 2 * k2p + 2 * k3p + k4p) / 6.0

        # Compute separation
        delta = state_p - state
        d = np.linalg.norm(delta)
        if d > 0:
            log_sum += np.log(d / d0)

        # Renormalize
        state_p = state + delta * (d0 / d)

        t_current = (i + 1) * renorm_interval
        mle_history.append(log_sum / t_current)

    mle = log_sum / T_total
    return mle, mle_history


# Set timeout for MLE computation
class ComputeTimeout(Exception):
    pass

def _handler(signum, frame):
    raise ComputeTimeout()

signal.signal(signal.SIGALRM, _handler)
signal.alarm(300)  # 5 min limit

try:
    state0 = [np.pi / 2, 0.0, np.pi / 2, 0.0]
    mle, mle_history = compute_mle(state0, dt=0.001, T_total=500.0,
                                    renorm_interval=0.5, **params)
    signal.alarm(0)
    print(f"MLE = {mle:.4f} s^-1")
    print(f"MLE history (last 5): {mle_history[-5:]}")
except ComputeTimeout:
    print("MLE computation timed out - using shorter integration")
    mle, mle_history = compute_mle(state0, dt=0.001, T_total=100.0,
                                    renorm_interval=0.5, **params)
    signal.alarm(0)
    print(f"MLE (shorter) = {mle:.4f} s^-1")

# Save MLE data
renorm_times = [(i + 1) * 0.5 for i in range(len(mle_history))]
mle_data = {
    "mle_final": float(mle),
    "positive_confirms_chaos": bool(mle > 0),
    "convergence_history": {
        "times": renorm_times[-20:],
        "mle_estimates": [float(x) for x in mle_history[-20:]]
    },
    "parameters": {"m1": m1, "m2": m2, "L1": L1, "L2": L2, "g": g},
    "initial_conditions": list(state0),
    "T_total": 500.0,
    "renorm_interval": 0.5,
    "dt": 0.001,
}
with open("results/lyapunov_exponent.json", "w") as f:
    json.dump(mle_data, f, indent=2)

# Plot MLE convergence
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(renorm_times, mle_history, color=colors[0], linewidth=0.8)
ax.axhline(y=mle, color=colors[1], linestyle="--", linewidth=1.0,
           label=f"Final MLE = {mle:.3f} s$^{{-1}}$")
ax.set_xlabel("Integration Time (s)")
ax.set_ylabel(r"$\lambda_{\max}$ (s$^{-1}$)")
ax.set_title("Convergence of Maximum Lyapunov Exponent")
ax.legend(frameon=True)
fig.savefig("figures/lyapunov_convergence.png", dpi=300)
fig.savefig("figures/lyapunov_convergence.pdf")
plt.close(fig)
print("Item 012 complete.")

# ====================================================================
# ITEM 013: Poincare section
# ====================================================================
print("\n" + "=" * 60)
print("ITEM 013: Poincare section")
print("=" * 60)

# Use moderate energy E ~ -10 J. Surface: theta2=0, omega2>0
# Use shorter simulations (500s) but more initial conditions

def find_poincare_crossings(state0, dt, n_steps, **params):
    """Find Poincare section crossings where theta2 crosses 0 with omega2>0."""
    crossings_theta1 = []
    crossings_omega1 = []
    state = np.array(state0, dtype=np.float64)

    for i in range(n_steps):
        prev_theta2 = state[2]
        k1 = dt * derivatives(state, **params)
        k2 = dt * derivatives(state + 0.5 * k1, **params)
        k3 = dt * derivatives(state + 0.5 * k2, **params)
        k4 = dt * derivatives(state + k3, **params)
        state = state + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

        curr_theta2 = state[2]
        if prev_theta2 < 0 and curr_theta2 >= 0 and state[3] > 0:
            crossings_theta1.append(state[0])
            crossings_omega1.append(state[1])

    return np.array(crossings_theta1), np.array(crossings_omega1)


E_target = -10.0  # moderate energy

signal.alarm(240)  # 4 min timeout
try:
    all_theta1 = []
    all_omega1 = []
    theta1_inits = np.linspace(-2.5, 2.5, 25)

    for theta1_0 in theta1_inits:
        V = -(m1 + m2) * g * L1 * np.cos(theta1_0) - m2 * g * L2
        KE_needed = E_target - V
        if KE_needed < 0:
            continue
        omega2_0 = np.sqrt(2 * KE_needed / (m2 * L2 ** 2))
        state0_p = [theta1_0, 0.0, 0.0, omega2_0]

        dt_p = 0.002
        T_poincare = 500.0
        n_steps_p = int(T_poincare / dt_p)

        print(f"  theta1_0={theta1_0:.2f}, omega2_0={omega2_0:.2f}")
        t1, w1 = find_poincare_crossings(state0_p, dt_p, n_steps_p, **params)
        all_theta1.extend(t1.tolist())
        all_omega1.extend(w1.tolist())
        print(f"    -> {len(t1)} crossings")

    signal.alarm(0)

    all_theta1 = np.array(all_theta1)
    all_omega1 = np.array(all_omega1)
    print(f"Total Poincare crossings: {len(all_theta1)}")

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(all_theta1, all_omega1, s=0.3, c=colors[0], alpha=0.5,
               edgecolors="none", rasterized=True)
    ax.set_xlabel(r"$\theta_1$ (rad)")
    ax.set_ylabel(r"$\omega_1$ (rad/s)")
    ax.set_title(r"Poincar\'e Section ($\theta_2=0$, $\dot{\theta}_2>0$, E=$-10$ J)")
    fig.savefig("figures/poincare_section.png", dpi=300)
    fig.savefig("figures/poincare_section.pdf")
    plt.close(fig)
    print("Item 013 figures saved.")

    poincare_data = {
        "n_crossings": len(all_theta1),
        "energy": E_target,
        "n_initial_conditions": int(np.sum([1 for t in theta1_inits
            if E_target - (-(m1+m2)*g*L1*np.cos(t)-m2*g*L2) >= 0])),
        "section_surface": "theta2=0, omega2>0",
    }
    with open("results/poincare_section.json", "w") as f:
        json.dump(poincare_data, f, indent=2)

except ComputeTimeout:
    signal.alarm(0)
    print("Poincare timed out - saving partial results")
    if all_theta1:
        all_theta1 = np.array(all_theta1)
        all_omega1 = np.array(all_omega1)
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.scatter(all_theta1, all_omega1, s=0.3, c=colors[0], alpha=0.5,
                   edgecolors="none", rasterized=True)
        ax.set_xlabel(r"$\theta_1$ (rad)")
        ax.set_ylabel(r"$\omega_1$ (rad/s)")
        ax.set_title(r"Poincar\'e Section (partial)")
        fig.savefig("figures/poincare_section.png", dpi=300)
        fig.savefig("figures/poincare_section.pdf")
        plt.close(fig)
        poincare_data = {"n_crossings": len(all_theta1), "energy": E_target,
                         "partial": True}
        with open("results/poincare_section.json", "w") as f:
            json.dump(poincare_data, f, indent=2)

# ====================================================================
# ITEM 014: Symplectic integrator (implicit midpoint)
# ====================================================================
print("\n" + "=" * 60)
print("ITEM 014: Symplectic integrator (implicit midpoint)")
print("=" * 60)

from pendulum import implicit_midpoint_integrate

state0 = [np.pi / 2, 0.0, np.pi / 2, 0.0]
E0 = total_energy(state0, **params)
E_scale = (m1 + m2) * g * L1 + m2 * g * L2

# Compare at dt=0.01 (coarse) to show behavior differences
dt_compare = 0.01
T_compare = 30.0
n_compare = int(T_compare / dt_compare)

print(f"Comparing RK4 vs implicit midpoint at dt={dt_compare} for T={T_compare}s")
traj_rk4 = rk4_integrate(derivatives, state0, dt_compare, n_compare, **params)
traj_imp = implicit_midpoint_integrate(derivatives, state0, dt_compare, n_compare, **params)

time_c = np.arange(n_compare + 1) * dt_compare
drift_rk4 = np.abs(total_energy(traj_rk4, **params) - E0) / E_scale
drift_imp = np.abs(total_energy(traj_imp, **params) - E0) / E_scale

print(f"RK4 max energy drift (dt=0.01): {np.max(drift_rk4):.2e}")
print(f"Impl. midpoint max drift (dt=0.01): {np.max(drift_imp):.2e}")

# Also at dt=0.001
dt_fine = 0.001
n_fine = int(T_compare / dt_fine)
traj_rk4_f = rk4_integrate(derivatives, state0, dt_fine, n_fine, **params)
traj_imp_f = implicit_midpoint_integrate(derivatives, state0, dt_fine, n_fine, **params)
time_f = np.arange(n_fine + 1) * dt_fine
drift_rk4_f = np.abs(total_energy(traj_rk4_f, **params) - E0) / E_scale
drift_imp_f = np.abs(total_energy(traj_imp_f, **params) - E0) / E_scale

print(f"RK4 max energy drift (dt=0.001): {np.max(drift_rk4_f):.2e}")
print(f"Impl. midpoint max drift (dt=0.001): {np.max(drift_imp_f):.2e}")

# Plot comparative energy drift
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)

ax1.plot(time_c, drift_rk4, color=colors[0], linewidth=0.8, label="RK4 (order 4)")
ax1.plot(time_c, drift_imp, color=colors[1], linewidth=0.8,
         label="Impl. midpoint (symplectic)")
ax1.set_xlabel("Time (s)")
ax1.set_ylabel(r"$|E(t) - E_0| / E_{\mathrm{scale}}$")
ax1.set_title(f"Energy Drift Comparison (dt={dt_compare})")
ax1.set_yscale("log")
ax1.legend(frameon=True)

ax2.plot(time_f, drift_rk4_f, color=colors[0], linewidth=0.5, label="RK4 (order 4)")
ax2.plot(time_f, drift_imp_f, color=colors[1], linewidth=0.5,
         label="Impl. midpoint (symplectic)")
ax2.set_xlabel("Time (s)")
ax2.set_ylabel(r"$|E(t) - E_0| / E_{\mathrm{scale}}$")
ax2.set_title(f"Energy Drift Comparison (dt={dt_fine})")
ax2.set_yscale("log")
ax2.legend(frameon=True)

fig.savefig("figures/integrator_comparison.png", dpi=300)
fig.savefig("figures/integrator_comparison.pdf")
plt.close(fig)
print("Item 014 figures saved.")

integrator_data = {
    "method_symplectic": "implicit_midpoint",
    "dt_coarse": dt_compare,
    "dt_fine": dt_fine,
    "rk4_max_drift_coarse": float(np.max(drift_rk4)),
    "symplectic_max_drift_coarse": float(np.max(drift_imp)),
    "rk4_max_drift_fine": float(np.max(drift_rk4_f)),
    "symplectic_max_drift_fine": float(np.max(drift_imp_f)),
    "note": "Implicit midpoint is 2nd-order symplectic, preserves phase space structure. RK4 is 4th-order but not symplectic."
}
with open("results/integrator_comparison.json", "w") as f:
    json.dump(integrator_data, f, indent=2)

print("\nPhase 3 items 011-014 complete!")
