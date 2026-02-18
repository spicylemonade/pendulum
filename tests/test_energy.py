"""Test energy conservation for the double pendulum simulator."""
import numpy as np
from sim.pendulum import simulate, total_energy


def test_energy_conservation_rk45():
    """RK45 simulation preserves energy to within 1% over 30 seconds."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    state0 = [np.pi / 4, 0.0, np.pi / 2, 0.0]
    result = simulate(state0, params, (0, 30), 0.01)
    state_arr = np.array([
        result['theta1'], result['omega1'],
        result['theta2'], result['omega2'],
    ])
    E = total_energy(state_arr, params)
    E0 = E[0]
    max_drift_pct = np.max(np.abs(E - E0)) / np.abs(E0) * 100
    assert max_drift_pct < 1.0, f"Energy drift {max_drift_pct:.6f}% exceeds 1%"
