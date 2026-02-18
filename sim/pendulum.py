"""Double pendulum equations of motion and numerical integration.

Implements the Lagrangian-derived equations for a double pendulum system
with configurable masses, lengths, and gravitational acceleration.
"""
import numpy as np
from scipy.integrate import solve_ivp


def derivatives(state, t, params):
    """Compute time derivatives of the double pendulum state.

    Args:
        state: [theta1, omega1, theta2, omega2] angles and angular velocities.
        t: Current time (unused, required for ODE interface).
        params: Dict with keys 'm1', 'm2', 'l1', 'l2', 'g'.

    Returns:
        Array [dtheta1/dt, domega1/dt, dtheta2/dt, domega2/dt].
    """
    th1, w1, th2, w2 = state
    m1, m2, l1, l2, g = params['m1'], params['m2'], params['l1'], params['l2'], params['g']
    M = m1 + m2
    dth = th1 - th2
    s, c = np.sin(dth), np.cos(dth)
    den = 2 * m1 + m2 - m2 * np.cos(2 * dth)

    a1 = (-g * (2 * m1 + m2) * np.sin(th1) - m2 * g * np.sin(th1 - 2 * th2)
          - 2 * s * m2 * (w2**2 * l2 + w1**2 * l1 * c)) / (l1 * den)
    a2 = (2 * s * (w1**2 * l1 * M + g * M * np.cos(th1)
          + w2**2 * l2 * m2 * c)) / (l2 * den)
    return np.array([w1, a1, w2, a2])


def simulate(initial_state, params, t_span, dt):
    """Integrate the double pendulum equations using RK45.

    Args:
        initial_state: [theta1, omega1, theta2, omega2].
        params: Dict with keys 'm1', 'm2', 'l1', 'l2', 'g'.
        t_span: Tuple (t_start, t_end).
        dt: Output time step.

    Returns:
        Dict with keys 'time', 'theta1', 'omega1', 'theta2', 'omega2'.
    """
    t_eval = np.arange(t_span[0], t_span[1], dt)

    def rhs(t, y):
        return derivatives(y, t, params)

    sol = solve_ivp(rhs, t_span, initial_state, method='RK45',
                    t_eval=t_eval, rtol=1e-10, atol=1e-12)
    return {
        'time': sol.t,
        'theta1': sol.y[0], 'omega1': sol.y[1],
        'theta2': sol.y[2], 'omega2': sol.y[3],
    }


def simulate_symplectic(initial_state, params, t_span, dt):
    """Integrate using the implicit midpoint method (a symplectic integrator).

    The implicit midpoint rule is symplectic for general Hamiltonian systems,
    including those with position-dependent mass matrices like the double
    pendulum. See Hairer, Lubich & Wanner (2003, 2006).

    Args:
        initial_state: [theta1, omega1, theta2, omega2].
        params: Dict with keys 'm1', 'm2', 'l1', 'l2', 'g'.
        t_span: Tuple (t_start, t_end).
        dt: Fixed time step.

    Returns:
        Dict with keys 'time', 'theta1', 'omega1', 'theta2', 'omega2'.
    """
    from scipy.optimize import fsolve
    n_steps = int((t_span[1] - t_span[0]) / dt)
    y = np.array(initial_state, dtype=float)
    out = [y.copy()]

    for _ in range(n_steps - 1):
        y_n = y.copy()

        def residual(y_next):
            mid = 0.5 * (y_n + y_next)
            f_mid = derivatives(mid, 0, params)
            return y_next - y_n - dt * f_mid

        y = fsolve(residual, y_n + dt * derivatives(y_n, 0, params), full_output=False)
        out.append(y.copy())

    out = np.array(out)
    return {
        'time': np.linspace(t_span[0], t_span[0] + (n_steps - 1) * dt, n_steps),
        'theta1': out[:, 0], 'omega1': out[:, 1],
        'theta2': out[:, 2], 'omega2': out[:, 3],
    }


def total_energy(state, params):
    """Compute total mechanical energy of the double pendulum.

    Args:
        state: Array-like [theta1, omega1, theta2, omega2] or 2-D array
               with shape (4, N) for vectorized evaluation.
        params: Dict with keys 'm1', 'm2', 'l1', 'l2', 'g'.

    Returns:
        Total energy (scalar or 1-D array).
    """
    th1, w1, th2, w2 = state[0], state[1], state[2], state[3]
    m1, m2, l1, l2, g = params['m1'], params['m2'], params['l1'], params['l2'], params['g']
    M = m1 + m2
    T = (0.5 * M * l1**2 * w1**2 + 0.5 * m2 * l2**2 * w2**2
         + m2 * l1 * l2 * w1 * w2 * np.cos(th1 - th2))
    V = -M * g * l1 * np.cos(th1) - m2 * g * l2 * np.cos(th2)
    return T + V
