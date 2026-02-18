"""Analysis tools for the double pendulum: Lyapunov exponents and Poincare sections.

Implements the Benettin et al. (1980) algorithm for the largest Lyapunov exponent
and Poincare section construction via zero-crossing detection.
See sources.bib: benettin1980lyapunov, skokos2010lyapunov, stachowiak2006numerical.
"""
import numpy as np
from scipy.integrate import solve_ivp
from sim.pendulum import derivatives


def lyapunov_exponent(params, initial_state, t_total, dt):
    """Estimate the largest Lyapunov exponent using Benettin's algorithm.

    Evolves a reference trajectory and a nearby test trajectory, periodically
    renormalizing the separation to avoid overflow.

    Args:
        params: Dict with keys 'm1', 'm2', 'l1', 'l2', 'g'.
        initial_state: [theta1, omega1, theta2, omega2].
        t_total: Total integration time.
        dt: Integration step and renormalization interval.

    Returns:
        Estimated largest Lyapunov exponent (float, units 1/s).
    """
    d0 = 1e-9
    y_ref = np.array(initial_state, dtype=float)
    # Perturb in theta1 direction
    y_test = y_ref.copy()
    y_test[0] += d0

    def rhs(t, y):
        return derivatives(y, t, params)

    lyap_sum = 0.0
    n_renorm = 0
    t = 0.0
    renorm_interval = max(dt, 0.1)
    n_steps = int(t_total / renorm_interval)

    for _ in range(n_steps):
        sol_ref = solve_ivp(rhs, (t, t + renorm_interval), y_ref,
                            method='RK45', rtol=1e-10, atol=1e-12)
        sol_test = solve_ivp(rhs, (t, t + renorm_interval), y_test,
                             method='RK45', rtol=1e-10, atol=1e-12)
        y_ref = sol_ref.y[:, -1]
        y_test = sol_test.y[:, -1]
        t += renorm_interval

        delta = y_test - y_ref
        dist = np.linalg.norm(delta)
        if dist > 0:
            lyap_sum += np.log(dist / d0)
            n_renorm += 1
            y_test = y_ref + delta * (d0 / dist)

    return lyap_sum / (n_renorm * renorm_interval) if n_renorm > 0 else 0.0


def poincare_section(params, initial_state, t_total, dt):
    """Compute a Poincare section: record (theta2, omega2) when theta1 crosses zero.

    Detects zero-crossings of theta1 with positive omega1 (upward crossing)
    using linear interpolation. See Stachowiak & Okada (2006) in sources.bib.

    Args:
        params: Dict with keys 'm1', 'm2', 'l1', 'l2', 'g'.
        initial_state: [theta1, omega1, theta2, omega2].
        t_total: Total integration time.
        dt: Output time step.

    Returns:
        Dict with keys 'theta2' and 'omega2' (arrays of crossing values).
    """
    def rhs(t, y):
        return derivatives(y, t, params)

    t_eval = np.arange(0, t_total, dt)
    sol = solve_ivp(rhs, (0, t_total), initial_state, method='RK45',
                    t_eval=t_eval, rtol=1e-10, atol=1e-12)
    th1 = sol.y[0]
    w1 = sol.y[1]
    th2 = sol.y[2]
    w2 = sol.y[3]

    # Normalize theta1 to [-pi, pi]
    th1_norm = (th1 + np.pi) % (2 * np.pi) - np.pi

    crossings_th2 = []
    crossings_w2 = []
    for i in range(len(th1_norm) - 1):
        if th1_norm[i] <= 0 < th1_norm[i + 1] and w1[i] > 0:
            # Linear interpolation
            frac = -th1_norm[i] / (th1_norm[i + 1] - th1_norm[i])
            crossings_th2.append(th2[i] + frac * (th2[i + 1] - th2[i]))
            crossings_w2.append(w2[i] + frac * (w2[i + 1] - w2[i]))

    return {'theta2': np.array(crossings_th2), 'omega2': np.array(crossings_w2)}
