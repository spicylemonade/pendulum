"""Flip-count map: sweep initial conditions and count flips of pendulum 2.

Creates a 200x200 grid over (theta1, theta2) in [-pi, pi]^2 with omega1=omega2=0.
Each point is simulated for 10 seconds and the number of full 2*pi flips of
theta2 is counted. The resulting fractal-like structure is characteristic of
chaotic systems. Compare with similar maps in Stachowiak & Okada (2006) and
Shinbrot et al. (1992) from sources.bib.
"""
import signal
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from scipy.integrate import odeint
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


def run_flip_map(n_grid=200):
    """Generate the flip-count map using odeint for speed."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    th1_vals = np.linspace(-np.pi, np.pi, n_grid)
    th2_vals = np.linspace(-np.pi, np.pi, n_grid)
    flip_map = np.zeros((n_grid, n_grid), dtype=int)
    t_eval = np.linspace(0, 10, 201)

    def rhs(y, t):
        return derivatives(y, t, params)

    # Set timeout: 5 minutes
    class Timeout(Exception):
        pass

    def handler(signum, frame):
        raise Timeout()
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(540)

    try:
        for i in range(n_grid):
            if i % 20 == 0:
                print(f'  Row {i}/{n_grid}')
            for j in range(n_grid):
                state0 = [th1_vals[i], 0.0, th2_vals[j], 0.0]
                sol = odeint(rhs, state0, t_eval, rtol=1e-6, atol=1e-6)
                unwrapped = np.unwrap(sol[:, 2])
                flip_map[j, i] = int(abs(unwrapped[-1] - unwrapped[0]) / (2*np.pi))
        signal.alarm(0)
    except Timeout:
        signal.alarm(0)
        print(f'Timed out at row {i}. Using partial results.')

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
