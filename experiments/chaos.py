"""Investigate sensitivity to initial conditions in the double pendulum.

Demonstrates exponential divergence of nearby trajectories, a hallmark
of chaos. See Shinbrot et al. (1992) and Benettin et al. (1980) in sources.bib.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from sim.pendulum import simulate

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
mpl.rcParams.update({
    'figure.figsize': (8, 5), 'figure.dpi': 300,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.linewidth': 0.8, 'axes.labelsize': 13,
    'axes.titlesize': 14, 'axes.titleweight': 'bold',
    'xtick.labelsize': 11, 'ytick.labelsize': 11,
    'legend.fontsize': 11, 'legend.framealpha': 0.9,
    'legend.edgecolor': '0.8', 'font.family': 'serif',
    'grid.alpha': 0.3, 'grid.linewidth': 0.5,
    'savefig.bbox': 'tight', 'savefig.pad_inches': 0.1,
})


def run_chaos_experiment():
    """Run two simulations with 1e-9 rad difference in theta1."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    eps = 1e-9
    state_a = [2.0, 0.0, 2.0, 0.0]
    state_b = [2.0 + eps, 0.0, 2.0, 0.0]

    result_a = simulate(state_a, params, (0, 30), 0.001)
    result_b = simulate(state_b, params, (0, 30), 0.001)

    divergence = np.abs(result_a['theta1'] - result_b['theta1'])
    divergence = np.maximum(divergence, 1e-16)  # avoid log(0)

    colors = sns.color_palette("colorblind")
    fig, ax = plt.subplots()
    ax.semilogy(result_a['time'], divergence, color=colors[0], linewidth=1.0,
                label=r'$|\Delta\theta_1(t)|$')
    ax.axhline(eps, color=colors[2], linestyle=':', linewidth=0.8,
               label=r'Initial perturbation ($10^{-9}$ rad)')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel(r'$|\Delta\theta_1|$ (rad)')
    ax.set_title('Exponential Divergence of Nearby Trajectories')
    ax.legend(frameon=True, loc='lower right')
    ax.set_ylim(1e-16, 1e2)
    plt.savefig('figures/chaos_divergence.png', dpi=300)
    plt.savefig('figures/chaos_divergence.pdf')
    plt.close()
    print(f'Max divergence: {divergence.max():.4f} rad')
    print(f'Figure saved to figures/chaos_divergence.png')


if __name__ == '__main__':
    run_chaos_experiment()
