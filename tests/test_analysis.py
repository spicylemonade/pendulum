"""Tests for sim/analysis.py: Lyapunov exponent and Poincare section."""
import numpy as np
from sim.analysis import lyapunov_exponent, poincare_section


def test_lyapunov_positive_for_chaos():
    """Lyapunov exponent is positive for chaotic initial conditions."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    lam = lyapunov_exponent(params, [2.0, 0, 2.0, 0], t_total=20, dt=0.01)
    assert lam > 0.1, f"Lyapunov exponent {lam:.4f} should be positive"
    assert lam < 10.0, f"Lyapunov exponent {lam:.4f} unreasonably large"


def test_poincare_section_has_crossings():
    """Poincare section detects zero-crossings of theta1."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    result = poincare_section(params, [1.5, 0, 0.5, 0], t_total=50, dt=0.001)
    assert len(result['theta2']) > 0, "No Poincare crossings found"
    assert len(result['theta2']) == len(result['omega2'])
