# Survey of Existing Double Pendulum Simulators

## Comparison Table

| Feature | dassencio/double-pendulum | josmarcristello/Double-Pendulum-Simulation | SciPython Tutorial |
|---------|--------------------------|--------------------------------------------|--------------------|
| **Language** | Python 3 | Python 3 | Python 3 |
| **Integration Method** | RK4 (custom) | RK4 + Euler (custom) | scipy.integrate.odeint |
| **Formulation** | Lagrangian + Hamiltonian | Lagrangian (Euler-Lagrange) | Lagrangian |
| **Visualization** | matplotlib animation | matplotlib static + animation | matplotlib animation |
| **Lines of Code** | ~300 (two files) | ~400 (with report code) | ~100 (tutorial) |
| **Energy Check** | No | No | No |
| **Chaos Analysis** | No | No | No |
| **Symplectic Integrator** | No | No | No |
| **Lyapunov Exponent** | No | No | No |
| **License** | MIT | MIT | CC |
| **Citation** | [dassencio_double_pendulum] | [cristello_double_pendulum] | [scipython_double_pendulum] |

## Key Observations

1. **All use RK4 or scipy odeint**: None of the surveyed implementations use symplectic integrators, leaving a gap in long-term energy conservation.

2. **No chaos analysis tools**: None compute Lyapunov exponents, Poincare sections, or flip-count maps. This project fills that gap.

3. **Custom vs. library integration**: dassencio and cristello implement RK4 from scratch (~50 LOC each), while SciPython uses scipy's odeint. Using scipy.integrate.solve_ivp (successor to odeint) is preferred for adaptive step-size control and modern API.

4. **Visualization**: All use matplotlib; the SciPython tutorial is the most concise. FuncAnimation is the standard approach for pendulum animation.

## Design Choice Justification

**Language: Python**
- All surveyed implementations use Python, confirming it as the de facto standard for physics simulations at this scale.
- Rich ecosystem: NumPy for arrays, SciPy for ODE integration, Matplotlib for visualization.
- Rapid prototyping with minimal boilerplate.

**Integration Approach: scipy.integrate.solve_ivp (RK45) + custom symplectic Stormer-Verlet**
- RK45 via solve_ivp provides adaptive step-size control and is the standard for non-stiff ODEs [hairer2006geometric].
- Adding a symplectic integrator (Stormer-Verlet) addresses the gap identified above: long-term energy conservation for Hamiltonian systems [hairer2003geometric].
- This dual-integrator approach enables direct comparison of energy drift, which is a core research goal.

**Visualization: matplotlib with FuncAnimation**
- Consistent with all surveyed implementations.
- Supports both static plots and animated GIFs without additional dependencies.

## References

- [dassencio_double_pendulum] Dassencio. *Double Pendulum Simulator*. GitHub.
- [cristello_double_pendulum] Cristello. *Double Pendulum Simulation*. GitHub.
- [scipython_double_pendulum] SciPython. *The Double Pendulum*.
- [hairer2003geometric] Hairer et al. *Acta Numerica*, 2003.
- [hairer2006geometric] Hairer et al. *Geometric Numerical Integration*, Springer, 2006.
