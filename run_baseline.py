"""Run baseline double pendulum simulation and generate figures.

Executes items 008-010 of the research rubric:
- 30-second simulation with canonical initial conditions
- Energy conservation validation
- Trajectory, phase portrait, and tip trajectory plots
"""

import json
import numpy as np
from pendulum import derivatives, total_energy, rk4_integrate, cartesian_positions

# --- Simulation Parameters ---
m1, m2 = 1.0, 1.0       # kg
L1, L2 = 1.0, 1.0       # m
g = 9.81                  # m/s^2
dt = 0.001                # s
T_sim = 30.0              # s
n_steps = int(T_sim / dt)

# Initial conditions: theta1=pi/2, theta2=pi/2, omega1=omega2=0
state0 = [np.pi / 2, 0.0, np.pi / 2, 0.0]

params = dict(m1=m1, m2=m2, L1=L1, L2=L2, g=g)

# --- Run simulation ---
print(f"Running baseline simulation: T={T_sim}s, dt={dt}, n_steps={n_steps}")
trajectory = rk4_integrate(derivatives, state0, dt, n_steps, **params)
time = np.arange(n_steps + 1) * dt
print(f"Simulation complete. Trajectory shape: {trajectory.shape}")

# --- Save trajectory ---
np.savez_compressed(
    "results/baseline_trajectory.npz",
    time=time,
    trajectory=trajectory,
    params=np.array([m1, m2, L1, L2, g, dt, T_sim]),
)
print("Saved results/baseline_trajectory.npz")

# --- Energy conservation (item 009) ---
energies = total_energy(trajectory, **params)
E0 = energies[0]
# When E0 ~ 0, use characteristic energy scale |V_min| for normalization
# V_min = -(m1+m2)*g*L1 - m2*g*L2 (lowest potential energy)
E_scale = max(abs(E0), (m1 + m2) * g * L1 + m2 * g * L2)
energy_drift = np.abs(energies - E0) / E_scale
max_drift = np.max(energy_drift)
max_abs_drift = np.max(np.abs(energies - E0))
print(f"Initial energy: E0 = {E0:.10e} J")
print(f"Energy scale: {E_scale:.4f} J")
print(f"Max absolute energy drift: {max_abs_drift:.2e} J")
print(f"Max relative energy drift (vs scale): {max_drift:.2e}")

energy_data = {
    "E0": float(E0),
    "E_scale": float(E_scale),
    "max_absolute_drift": float(max_abs_drift),
    "max_relative_drift": float(max_drift),
    "drift_below_1e-4": bool(max_drift < 1e-4),
    "dt": dt,
    "T_sim": T_sim,
    "n_steps": n_steps,
}
with open("results/energy_conservation.json", "w") as f:
    json.dump(energy_data, f, indent=2)
print(f"Energy drift < 1e-4: {max_drift < 1e-4}")

# --- Figures (item 010) ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
mpl.rcParams.update({
    "figure.figsize": (8, 5),
    "figure.dpi": 300,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "axes.labelsize": 13,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 11,
    "legend.framealpha": 0.9,
    "legend.edgecolor": "0.8",
    "font.family": "serif",
    "grid.alpha": 0.3,
    "grid.linewidth": 0.5,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
})

colors = sns.color_palette("colorblind")

# Plot 1: theta1 and theta2 vs time
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(time, trajectory[:, 0], color=colors[0], linewidth=0.5, label=r"$\theta_1$")
ax.plot(time, trajectory[:, 2], color=colors[1], linewidth=0.5, label=r"$\theta_2$")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Angle (rad)")
ax.set_title("Double Pendulum Angular Displacement")
ax.legend(loc="upper right", frameon=True)
fig.savefig("figures/theta_vs_time.png", dpi=300)
fig.savefig("figures/theta_vs_time.pdf")
plt.close(fig)
print("Saved figures/theta_vs_time.png")

# Plot 2: Cartesian trajectory of pendulum tip
x1, y1, x2, y2 = cartesian_positions(trajectory, L1, L2)
fig, ax = plt.subplots(figsize=(7, 7))
ax.plot(x2, y2, color=colors[2], linewidth=0.1, alpha=0.6)
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.set_title("Trajectory of Second Pendulum Bob")
ax.set_aspect("equal")
fig.savefig("figures/tip_trajectory.png", dpi=300)
fig.savefig("figures/tip_trajectory.pdf")
plt.close(fig)
print("Saved figures/tip_trajectory.png")

# Plot 3: Phase portraits
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
ax1.plot(trajectory[:, 0], trajectory[:, 1], color=colors[0], linewidth=0.15, alpha=0.7)
ax1.set_xlabel(r"$\theta_1$ (rad)")
ax1.set_ylabel(r"$\omega_1$ (rad/s)")
ax1.set_title(r"Phase Portrait: Pendulum 1")

ax2.plot(trajectory[:, 2], trajectory[:, 3], color=colors[1], linewidth=0.15, alpha=0.7)
ax2.set_xlabel(r"$\theta_2$ (rad)")
ax2.set_ylabel(r"$\omega_2$ (rad/s)")
ax2.set_title(r"Phase Portrait: Pendulum 2")

fig.savefig("figures/phase_portraits.png", dpi=300)
fig.savefig("figures/phase_portraits.pdf")
plt.close(fig)
print("Saved figures/phase_portraits.png")

# Plot 4: Energy vs time
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(time, energy_drift, color=colors[3], linewidth=0.5)
ax.set_xlabel("Time (s)")
ax.set_ylabel(r"$|E(t) - E_0| / E_{\mathrm{scale}}$")
ax.set_title("Relative Energy Drift (RK4, dt=0.001)")
ax.set_yscale("log")
fig.savefig("figures/energy_drift.png", dpi=300)
fig.savefig("figures/energy_drift.pdf")
plt.close(fig)
print("Saved figures/energy_drift.png")

print("\nAll baseline tasks complete!")
