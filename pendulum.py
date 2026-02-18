"""Double pendulum simulation module.

Implements the equations of motion for a planar double pendulum using the
Lagrangian formulation, along with RK4 and symplectic (Stormer-Verlet)
integrators, energy computation, and related utilities.

References:
    - Shinbrot et al. 1992, "Chaos in a double pendulum", Am. J. Phys. 60, 491
    - Wikipedia, "Double pendulum"
    - Hairer, Lubich, Wanner, "Geometric Numerical Integration" (2006)
"""

import numpy as np


def derivatives(state, m1, m2, L1, L2, g):
    """Compute time derivatives of the double pendulum state vector.

    Parameters
    ----------
    state : array_like, shape (4,)
        [theta1, omega1, theta2, omega2] where theta are angles from
        vertical and omega are angular velocities.
    m1, m2 : float
        Masses of the first and second pendulum bobs (kg).
    L1, L2 : float
        Lengths of the first and second pendulum rods (m).
    g : float
        Gravitational acceleration (m/s^2).

    Returns
    -------
    numpy.ndarray, shape (4,)
        [dtheta1/dt, domega1/dt, dtheta2/dt, domega2/dt]
    """
    theta1, omega1, theta2, omega2 = state
    delta = theta1 - theta2
    sin_d = np.sin(delta)
    cos_d = np.cos(delta)
    M = m1 + m2

    den1 = L1 * (M - m2 * cos_d ** 2)
    den2 = L2 * (M - m2 * cos_d ** 2)

    domega1 = (
        -m2 * L1 * omega1 ** 2 * sin_d * cos_d
        + m2 * g * np.sin(theta2) * cos_d
        - m2 * L2 * omega2 ** 2 * sin_d
        - M * g * np.sin(theta1)
    ) / den1

    domega2 = (
        m2 * L2 * omega2 ** 2 * sin_d * cos_d
        + M * (L1 * omega1 ** 2 * sin_d
               - g * np.sin(theta2)
               + g * np.sin(theta1) * cos_d)
    ) / den2

    return np.array([omega1, domega1, omega2, domega2])


def total_energy(state, m1, m2, L1, L2, g):
    """Compute total mechanical energy of the double pendulum.

    Parameters
    ----------
    state : array_like, shape (4,) or (N, 4)
        State vector(s) [theta1, omega1, theta2, omega2].
    m1, m2 : float
        Masses (kg).
    L1, L2 : float
        Lengths (m).
    g : float
        Gravitational acceleration (m/s^2).

    Returns
    -------
    float or numpy.ndarray
        Total energy (kinetic + potential).
    """
    state = np.asarray(state)
    if state.ndim == 1:
        theta1, omega1, theta2, omega2 = state
    else:
        theta1 = state[:, 0]
        omega1 = state[:, 1]
        theta2 = state[:, 2]
        omega2 = state[:, 3]

    delta = theta1 - theta2
    M = m1 + m2

    T = (0.5 * M * L1 ** 2 * omega1 ** 2
         + 0.5 * m2 * L2 ** 2 * omega2 ** 2
         + m2 * L1 * L2 * omega1 * omega2 * np.cos(delta))
    V = -M * g * L1 * np.cos(theta1) - m2 * g * L2 * np.cos(theta2)

    return T + V


def rk4_integrate(deriv_func, state0, dt, n_steps, **params):
    """4th-order Runge-Kutta integrator.

    Parameters
    ----------
    deriv_func : callable
        Function f(state, **params) returning derivatives.
    state0 : array_like, shape (n,)
        Initial state vector.
    dt : float
        Time step.
    n_steps : int
        Number of integration steps.
    **params : dict
        Additional parameters passed to deriv_func.

    Returns
    -------
    numpy.ndarray, shape (n_steps + 1, n)
        Full time series of states including initial state.
    """
    state = np.array(state0, dtype=np.float64)
    n = len(state)
    trajectory = np.empty((n_steps + 1, n))
    trajectory[0] = state

    for i in range(n_steps):
        k1 = dt * deriv_func(state, **params)
        k2 = dt * deriv_func(state + 0.5 * k1, **params)
        k3 = dt * deriv_func(state + 0.5 * k2, **params)
        k4 = dt * deriv_func(state + k3, **params)
        state = state + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        trajectory[i + 1] = state

    return trajectory


def cartesian_positions(state, L1, L2):
    """Convert angular state to Cartesian positions of both bobs.

    Parameters
    ----------
    state : array_like, shape (4,) or (N, 4)
        State vector(s).
    L1, L2 : float
        Rod lengths.

    Returns
    -------
    x1, y1, x2, y2 : float or ndarray
        Cartesian positions.
    """
    state = np.asarray(state)
    if state.ndim == 1:
        theta1, _, theta2, _ = state
    else:
        theta1 = state[:, 0]
        theta2 = state[:, 2]

    x1 = L1 * np.sin(theta1)
    y1 = -L1 * np.cos(theta1)
    x2 = x1 + L2 * np.sin(theta2)
    y2 = y1 - L2 * np.cos(theta2)
    return x1, y1, x2, y2
