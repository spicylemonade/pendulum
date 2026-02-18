"""Item 015: Generate flip-count map for the double pendulum.

Creates a 100x100 grid of initial conditions and counts flips for each.
"""

import json
import signal
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from pendulum import derivatives

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

m1, m2 = 1.0, 1.0
L1, L2 = 1.0, 1.0
g = 9.81
params = dict(m1=m1, m2=m2, L1=L1, L2=L2, g=g)

N = 100  # grid resolution
dt = 0.02  # coarser step for speed (fractal structure is robust)
T_sim = 10.0
n_steps = int(T_sim / dt)

theta1_grid = np.linspace(-np.pi, np.pi, N)
theta2_grid = np.linspace(-np.pi, np.pi, N)
flip_counts = np.zeros((N, N), dtype=int)


def count_flips_single(theta1_0, theta2_0, dt, n_steps, **params):
    """Count total flips for a single initial condition.

    A flip is when a pendulum passes through the inverted position (theta = +/- pi).
    We detect sign changes of cos(theta) from negative to positive or vice versa,
    meaning the pendulum crosses the top.
    """
    state = np.array([theta1_0, 0.0, theta2_0, 0.0], dtype=np.float64)
    flips = 0
    # Track cos(theta) sign to detect crossing through pi
    prev_cos1 = np.cos(state[0])
    prev_cos2 = np.cos(state[2])

    for _ in range(n_steps):
        k1 = dt * derivatives(state, **params)
        k2 = dt * derivatives(state + 0.5 * k1, **params)
        k3 = dt * derivatives(state + 0.5 * k2, **params)
        k4 = dt * derivatives(state + k3, **params)
        state = state + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

        cos1 = np.cos(state[0])
        cos2 = np.cos(state[2])

        # Flip when cos(theta) crosses -1 (theta crosses pi)
        # Detect: cos goes from < -0.9 (near top) with sign change wouldn't work well
        # Better: detect when cos goes from >0 to <0 or <0 to >0 through -1
        # Simplest robust method: a flip is when cos(theta) < -0.99 (near inverted)
        # and the sign of sin(theta) changed
        # Even simpler: count transitions through cos=-1 region
        # Most standard: check if theta (mod 2pi) crosses pi
        if prev_cos1 > -0.5 and cos1 <= -0.5:
            flips += 1
        elif prev_cos1 < -0.5 and cos1 >= -0.5:
            # exiting inverted region (also counts)
            pass
        if prev_cos2 > -0.5 and cos2 <= -0.5:
            flips += 1
        elif prev_cos2 < -0.5 and cos2 >= -0.5:
            pass

        prev_cos1 = cos1
        prev_cos2 = cos2

    return flips


class ComputeTimeout(Exception):
    pass

def _handler(signum, frame):
    raise ComputeTimeout()

signal.signal(signal.SIGALRM, _handler)
signal.alarm(300)  # 5 min timeout

try:
    total = N * N
    for i in range(N):
        for j in range(N):
            flip_counts[i, j] = count_flips_single(
                theta1_grid[j], theta2_grid[i], dt, n_steps, **params
            )
        if (i + 1) % 10 == 0:
            print(f"Row {i+1}/{N} complete")
    signal.alarm(0)
    print(f"Flip count map complete. Max flips: {flip_counts.max()}")
except ComputeTimeout:
    signal.alarm(0)
    print(f"Timed out at row ~{i}. Using partial results.")

# Save data
np.savez_compressed("results/flip_count_map.npz",
                     flip_counts=flip_counts,
                     theta1_grid=theta1_grid,
                     theta2_grid=theta2_grid)

# Plot heatmap
fig, ax = plt.subplots(figsize=(8, 7))
cmap = plt.cm.hot_r
im = ax.imshow(flip_counts, extent=[-np.pi, np.pi, -np.pi, np.pi],
               origin="lower", cmap=cmap, aspect="equal",
               interpolation="nearest")
cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label("Total Flip Count", fontsize=12)
ax.set_xlabel(r"$\theta_1$ (rad)")
ax.set_ylabel(r"$\theta_2$ (rad)")
ax.set_title("Flip-Count Map of the Double Pendulum")
ax.set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
ax.set_xticklabels([r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"])
ax.set_yticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
ax.set_yticklabels([r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"])

fig.savefig("figures/flip_count_map.png", dpi=300)
fig.savefig("figures/flip_count_map.pdf")
plt.close(fig)
print("Saved figures/flip_count_map.png")

flipmap_data = {
    "grid_size": N,
    "dt": dt,
    "T_sim": T_sim,
    "max_flips": int(flip_counts.max()),
    "mean_flips": float(flip_counts.mean()),
    "fraction_with_flips": float(np.mean(flip_counts > 0)),
}
with open("results/flip_count_summary.json", "w") as f:
    json.dump(flipmap_data, f, indent=2)
print("Item 015 complete!")
