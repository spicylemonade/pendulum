"""Benchmark wall-clock time and energy drift for the RK45 integrator."""
import json
import time
import numpy as np
from sim.pendulum import simulate, total_energy


def run_benchmark():
    """Run baseline benchmark: 100s simulation with dt=0.001."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    state0 = [np.pi / 4, 0.0, np.pi / 2, 0.0]
    sim_time = 100.0
    dt = 0.001

    t0 = time.perf_counter()
    result = simulate(state0, params, (0, sim_time), dt)
    wall_time = time.perf_counter() - t0

    state_arr = np.array([
        result['theta1'], result['omega1'],
        result['theta2'], result['omega2'],
    ])
    E = total_energy(state_arr, params)
    E0 = E[0]
    max_drift_pct = float(np.max(np.abs(E - E0)) / np.abs(E0) * 100)

    bench = {
        'method': 'RK45',
        'sim_time_sec': sim_time,
        'wall_time_sec': round(wall_time, 4),
        'n_steps': len(result['time']),
        'max_energy_drift_pct': max_drift_pct,
    }
    with open('results/baseline_benchmarks.json', 'w') as f:
        json.dump(bench, f, indent=2)
    print(json.dumps(bench, indent=2))
    return bench


if __name__ == '__main__':
    run_benchmark()
