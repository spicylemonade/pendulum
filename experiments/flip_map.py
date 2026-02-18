"""Flip-count map: sweep initial conditions and count flips of pendulum 2.

Creates a 200x200 grid over (theta1, theta2) in [-pi, pi]^2 with omega1=omega2=0.
Each point is simulated for 10 seconds and the number of full 2*pi flips of
theta2 is counted. The resulting fractal-like structure is characteristic of
chaotic systems. Compare with similar maps in Stachowiak & Okada (2006) and
Shinbrot et al. (1992) from sources.bib.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from scipy.integrate import solve_ivp
from sim.pendulum import derivatives

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
mpl.rcParams.update({
    'figure.figsize': (8, 7), 'figure.dpi': 300,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.linewidth': 0.8, 'axes.labelsize': 13,
    'axes.titlesize': 14, 'axes.titleweight': 'bold',
    'xtick.labelsize': 11, 'ytick.labelsize': 11,
    'legend.fontsize': 11, 'legend.framealpha': 0.9,
    'legend.edgecolor': '0.8', 'font.family': 'serif',
    'grid.alpha': 0.3, 'grid.linewidth': 0.5,
    'savefig.bbox': 'tight', 'savefig.pad_inches': 0.1,
})


def count_flips(th2_arr):
    """Count full 2*pi flips of theta2 by tracking cumulative angle."""
    unwrapped = np.unwrap(th2_arr)
    total_rotation = unwrapped[-1] - unwrapped[0]
    return int(abs(total_rotation) / (2 * np.pi))


def run_flip_map(n_grid=200):
    """Generate the flip-count map."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    th1_vals = np.linspace(-np.pi, np.pi, n_grid)
    th2_vals = np.linspace(-np.pi, np.pi, n_grid)
    flip_map = np.zeros((n_grid, n_grid), dtype=int)

    def rhs(t, y):
        return derivatives(y, t, params)

    total = n_grid * n_grid
    for i, th1 in enumerate(th1_vals):
        if i % 20 == 0:
            print(f'  Row {i}/{n_grid} ({100*i*n_grid/total:.0f}%)')
        for j, th2 in enumerate(th2_vals):
            state0 = [th1, 0.0, th2, 0.0]
            sol = solve_ivp(rhs, (0, 10), state0, method='RK45',
                            rtol=1e-8, atol=1e-10, max_step=0.1)
            flip_map[j, i] = count_flips(sol.y[2])

    fig, ax = plt.subplots(figsize=(8, 7))
    cmap = sns.color_palette("rocket", as_cmap=True)
    im = ax.imshow(flip_map, extent=[-np.pi, np.pi, -np.pi, np.pi],
                   origin='lower', aspect='equal', cmap=cmap,
                   interpolation='nearest')
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Number of full flips')
    ax.set_xlabel(r'$\theta_1$ (rad)')
    ax.set_ylabel(r'$\theta_2$ (rad)')
    ax.set_title('Flip-Count Map of the Double Pendulum')
    plt.savefig('figures/flip_count_map.png', dpi=300)
    plt.savefig('figures/flip_count_map.pdf')
    plt.close()
    print(f'Flip map saved. Max flips: {flip_map.max()}')


if __name__ == '__main__':
    run_flip_map()
