"""Compare RK45 vs symplectic integrator across step sizes.

References Hairer, Lubich & Wanner (2003, 2006) from sources.bib for
integrator theory and comparison methodology.
"""
import json
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from sim.pendulum import simulate, simulate_symplectic, total_energy

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
mpl.rcParams.update({'figure.figsize': (10, 5), 'figure.dpi': 300, 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.linewidth': 0.8, 'axes.labelsize': 13,
    'axes.titlesize': 14, 'axes.titleweight': 'bold', 'xtick.labelsize': 11,
    'ytick.labelsize': 11, 'legend.fontsize': 11, 'legend.framealpha': 0.9,
    'legend.edgecolor': '0.8', 'font.family': 'serif', 'grid.alpha': 0.3,
    'grid.linewidth': 0.5, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.1})


def run_comparison():
    """Run both integrators at multiple dt values."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    state0 = [np.pi / 4, 0.0, np.pi / 2, 0.0]
    dt_values = [0.1, 0.01, 0.001]
    results = {}

    for dt in dt_values:
        for method, sim_fn in [('RK45', simulate), ('Symplectic', simulate_symplectic)]:
            t0 = time.perf_counter()
            r = sim_fn(state0, params, (0, 100), dt)
            wall = time.perf_counter() - t0
            E = total_energy(np.array([r['theta1'], r['omega1'],
                                       r['theta2'], r['omega2']]), params)
            drift = float(np.max(np.abs(E - E[0])) / np.abs(E[0]) * 100)
            key = f'{method}_dt{dt}'
            results[key] = {
                'method': method, 'dt': dt, 'wall_time_sec': round(wall, 4),
                'max_energy_drift_pct': drift, 'n_steps': len(r['time']),
            }
            print(f'{key}: wall={wall:.3f}s, drift={drift:.8f}%')

    with open('results/integrator_comparison.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Plot
    colors = sns.color_palette("colorblind")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    for idx, method in enumerate(['RK45', 'Symplectic']):
        dts = [r['dt'] for r in results.values() if r['method'] == method]
        drifts = [r['max_energy_drift_pct'] for r in results.values() if r['method'] == method]
        walls = [r['wall_time_sec'] for r in results.values() if r['method'] == method]
        marker = 'o' if idx == 0 else 's'
        ax1.loglog(dts, [max(d, 1e-12) for d in drifts], f'-{marker}',
                   color=colors[idx], label=method, linewidth=1.5, markersize=8)
        ax2.loglog(dts, walls, f'-{marker}', color=colors[idx],
                   label=method, linewidth=1.5, markersize=8)

    ax1.set_xlabel('Step size dt (s)')
    ax1.set_ylabel('Max energy drift (%)')
    ax1.set_title('Energy Conservation vs Step Size')
    ax1.legend(frameon=True)
    ax1.invert_xaxis()

    ax2.set_xlabel('Step size dt (s)')
    ax2.set_ylabel('Wall-clock time (s)')
    ax2.set_title('Computation Cost vs Step Size')
    ax2.legend(frameon=True)
    ax2.invert_xaxis()

    plt.savefig('figures/integrator_comparison.png', dpi=300)
    plt.savefig('figures/integrator_comparison.pdf')
    plt.close()
    print('Comparison complete.')


if __name__ == '__main__':
    run_comparison()
