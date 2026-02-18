"""Visualization functions for the double pendulum simulator."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from matplotlib.animation import FuncAnimation


def _setup_style():
    """Configure publication-quality matplotlib styling."""
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


def plot_trajectories(result, savepath='figures/baseline_trajectory'):
    """Plot angle trajectories and phase portrait.

    Args:
        result: Dict from simulate() with keys time, theta1, omega1, theta2, omega2.
        savepath: Base path for saving (without extension).
    """
    _setup_style()
    colors = sns.color_palette("colorblind")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), constrained_layout=True)

    ax1.plot(result['time'], result['theta1'], color=colors[0],
             label=r'$\theta_1$', linewidth=1.2)
    ax1.plot(result['time'], result['theta2'], color=colors[1],
             label=r'$\theta_2$', linewidth=1.2, linestyle='--')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Angle (rad)')
    ax1.set_title('Double Pendulum Angle Trajectories')
    ax1.legend(frameon=True)

    ax2.plot(result['theta1'], result['omega1'], color=colors[2],
             linewidth=0.5, alpha=0.8)
    ax2.set_xlabel(r'$\theta_1$ (rad)')
    ax2.set_ylabel(r'$\dot{\theta}_1$ (rad/s)')
    ax2.set_title('Phase Portrait')

    plt.savefig(f'{savepath}.png', dpi=300)
    plt.savefig(f'{savepath}.pdf')
    plt.close()


def animate_pendulum(result, params, savepath='figures/pendulum_animation.gif',
                     skip=10):
    """Create animated GIF of the double pendulum.

    Args:
        result: Dict from simulate().
        params: Dict with 'l1', 'l2'.
        savepath: Output GIF path.
        skip: Frame skip factor for speed.
    """
    _setup_style()
    l1, l2 = params['l1'], params['l2']
    th1, th2 = result['theta1'][::skip], result['theta2'][::skip]
    x1 = l1 * np.sin(th1)
    y1 = -l1 * np.cos(th1)
    x2 = x1 + l2 * np.sin(th2)
    y2 = y1 - l2 * np.cos(th2)

    fig, ax = plt.subplots(figsize=(6, 6))
    lim = 1.1 * (l1 + l2)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect('equal')
    ax.set_title('Double Pendulum')
    ax.grid(True, alpha=0.3)

    colors = sns.color_palette("colorblind")
    line, = ax.plot([], [], 'o-', color=colors[0], linewidth=2, markersize=8)
    trail, = ax.plot([], [], '-', color=colors[1], linewidth=0.5, alpha=0.4)
    trail_x, trail_y = [], []

    def update(i):
        line.set_data([0, x1[i], x2[i]], [0, y1[i], y2[i]])
        trail_x.append(x2[i])
        trail_y.append(y2[i])
        trail.set_data(trail_x, trail_y)
        return line, trail

    anim = FuncAnimation(fig, update, frames=len(th1), interval=30, blit=True)
    anim.save(savepath, writer='pillow', fps=30)
    plt.close()
