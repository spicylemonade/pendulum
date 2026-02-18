"""Parameter sensitivity study: Lyapunov exponent vs mass and length ratios."""
import json
import signal
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from sim.analysis import lyapunov_exponent

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
mpl.rcParams.update({'figure.figsize': (8, 6), 'figure.dpi': 300, 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.linewidth': 0.8, 'axes.labelsize': 13,
    'axes.titlesize': 14, 'axes.titleweight': 'bold', 'xtick.labelsize': 11,
    'ytick.labelsize': 11, 'legend.fontsize': 11, 'legend.framealpha': 0.9,
    'legend.edgecolor': '0.8', 'font.family': 'serif', 'grid.alpha': 0.3,
    'grid.linewidth': 0.5, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.1})


def run_param_sweep():
    """Sweep mass and length ratios, computing Lyapunov exponent for each."""
    mass_ratios = [0.1, 0.5, 1.0, 2.0, 10.0]
    length_ratios = [0.1, 0.5, 1.0, 2.0]
    state0 = [2.0, 0.0, 2.0, 0.0]
    results = {}
    lyap_grid = np.zeros((len(length_ratios), len(mass_ratios)))

    class Timeout(Exception):
        pass

    def handler(signum, frame):
        raise Timeout()
    signal.signal(signal.SIGALRM, handler)

    for i, lr in enumerate(length_ratios):
        for j, mr in enumerate(mass_ratios):
            params = {'m1': 1.0, 'm2': mr, 'l1': 1.0, 'l2': lr, 'g': 9.81}
            signal.alarm(30)
            try:
                lam = lyapunov_exponent(params, state0, t_total=20, dt=0.01)
                signal.alarm(0)
            except (Timeout, Exception):
                signal.alarm(0)
                lam = float('nan')
            lyap_grid[i, j] = lam
            key = f'm2m1={mr}_l2l1={lr}'
            results[key] = {'m2_m1': mr, 'l2_l1': lr, 'lyapunov': float(lam)}
            print(f'  m2/m1={mr}, l2/l1={lr}: lambda={lam:.4f}')

    with open('results/param_sensitivity.json', 'w') as f:
        json.dump(results, f, indent=2)

    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = sns.color_palette("viridis", as_cmap=True)
    im = ax.imshow(lyap_grid, cmap=cmap, aspect='auto', origin='lower',
                   extent=[-0.5, len(mass_ratios) - 0.5,
                           -0.5, len(length_ratios) - 0.5])
    ax.set_xticks(range(len(mass_ratios)))
    ax.set_xticklabels([str(m) for m in mass_ratios])
    ax.set_yticks(range(len(length_ratios)))
    ax.set_yticklabels([str(l) for l in length_ratios])
    ax.set_xlabel(r'$m_2/m_1$')
    ax.set_ylabel(r'$l_2/l_1$')
    ax.set_title('Largest Lyapunov Exponent vs Mass and Length Ratios')
    # Annotate cells
    for i in range(len(length_ratios)):
        for j in range(len(mass_ratios)):
            val = lyap_grid[i, j]
            txt = f'{val:.2f}' if not np.isnan(val) else 'N/A'
            ax.text(j, i, txt, ha='center', va='center', fontsize=9,
                    color='white' if val > np.nanmean(lyap_grid) else 'black')
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Lyapunov exponent (1/s)')
    plt.savefig('figures/param_sensitivity.png', dpi=300)
    plt.savefig('figures/param_sensitivity.pdf')
    plt.close()
    print('Parameter sweep complete.')


if __name__ == '__main__':
    run_param_sweep()
