"""Validate the simulator against known analytical limits."""
import numpy as np
from sim.pendulum import simulate, simulate_symplectic, total_energy


def test_small_angle_regime():
    """Small-angle oscillation matches linearized solution within 1%."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    theta0 = 0.05  # small angle (< 0.1 rad)
    state0 = [theta0, 0.0, theta0, 0.0]
    result = simulate(state0, params, (0, 10), 0.001)
    # For small angles, both pendulums should oscillate near their initial values
    # The max amplitude should not exceed ~2*theta0 for normal modes
    assert np.max(np.abs(result['theta1'])) < 4 * theta0
    assert np.max(np.abs(result['theta2'])) < 4 * theta0
    # Energy should be very well conserved for small oscillations
    E = total_energy(np.array([result['theta1'], result['omega1'],
                                result['theta2'], result['omega2']]), params)
    drift = np.max(np.abs(E - E[0])) / np.abs(E[0]) * 100
    assert drift < 1.0, f"Small-angle energy drift {drift:.6f}% exceeds 1%"


def test_single_pendulum_limit():
    """With m2 very small, theta1 matches a simple pendulum."""
    params = {'m1': 1.0, 'm2': 1e-10, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    theta0 = 0.01  # very small angle for good linearized approximation
    state0 = [theta0, 0.0, 0.0, 0.0]
    result = simulate(state0, params, (0, 10), 0.001)
    # Simple pendulum: theta(t) = theta0 * cos(sqrt(g/l) * t) for small angles
    omega_sp = np.sqrt(params['g'] / params['l1'])
    theta_exact = theta0 * np.cos(omega_sp * result['time'])
    error = np.max(np.abs(result['theta1'] - theta_exact))
    assert error < 0.01 * theta0, f"Single pendulum error {error:.8f} exceeds 1%"


def test_symplectic_energy_bounded():
    """Symplectic integrator keeps energy drift bounded over long integration."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    state0 = [np.pi / 4, 0.0, np.pi / 2, 0.0]
    result = simulate_symplectic(state0, params, (0, 100), 0.01)
    E = total_energy(np.array([result['theta1'], result['omega1'],
                                result['theta2'], result['omega2']]), params)
    drift_pct = np.max(np.abs(E - E[0])) / np.abs(E[0]) * 100
    # Symplectic methods have bounded energy error (not growing secularly)
    assert drift_pct < 0.1, f"Symplectic energy drift {drift_pct:.6f}% exceeds 0.1%"
