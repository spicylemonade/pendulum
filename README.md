# Double Pendulum Simulator

A minimal double pendulum simulator using Lagrangian mechanics with numerical integration, chaos analysis, and publication-quality visualization. The project implements both RK45 (adaptive) and symplectic (implicit midpoint) integrators, computes Lyapunov exponents, generates Poincare sections, and produces flip-count basin maps to characterize the chaotic dynamics of the system.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run a basic simulation and plot trajectories

```python
import numpy as np
from sim.pendulum import simulate, total_energy
from sim.visualize import plot_trajectories

params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
state0 = [np.pi/4, 0.0, np.pi/2, 0.0]  # [theta1, omega1, theta2, omega2]
result = simulate(state0, params, (0, 30), 0.01)
plot_trajectories(result)
```

### Generate an animation

```python
from sim.visualize import animate_pendulum
animate_pendulum(result, params)  # saves figures/pendulum_animation.gif
```

### Symplectic integration

```python
from sim.pendulum import simulate_symplectic
result_s = simulate_symplectic(state0, params, (0, 100), 0.01)
```

### Compute Lyapunov exponent

```python
from sim.analysis import lyapunov_exponent
lam = lyapunov_exponent(params, state0, t_total=50, dt=0.01)
print(f'Largest Lyapunov exponent: {lam:.4f} /s')
```

### Run experiments

```bash
python -m experiments.chaos              # sensitivity to initial conditions
python -m experiments.compare_integrators # RK45 vs symplectic comparison
python -m experiments.param_sweep        # parameter sensitivity heatmap
python -m experiments.flip_map           # flip-count basin map
python -m benchmarks.timing              # performance benchmarks
python -m benchmarks.profile             # profiling analysis
```

### Run tests

```bash
pytest tests/ -v --cov=sim
```

## Project Structure

```
sim/
  pendulum.py    - Equations of motion, RK45/symplectic integration, energy
  analysis.py    - Lyapunov exponent (Benettin), Poincare section
  visualize.py   - Trajectory plots and animation
tests/
  test_energy.py    - Energy conservation test
  test_limits.py    - Analytical limit validation (3 tests)
  test_analysis.py  - Lyapunov and Poincare tests
  test_visualize.py - Plot/animation generation tests
experiments/
  chaos.py                - Initial condition sensitivity
  compare_integrators.py  - RK45 vs symplectic comparison
  param_sweep.py          - Mass/length ratio Lyapunov heatmap
  flip_map.py             - Flip-count basin map
benchmarks/
  timing.py   - Wall-clock benchmarks
  profile.py  - cProfile analysis
docs/
  equations.md - Full Lagrangian derivation
  survey.md    - Existing simulator comparison
  scope.md     - Project scope
  report.md    - Summary report
results/       - JSON experiment outputs
figures/       - Publication-quality PNG/PDF figures
```

## References

1. Goldstein, H., Poole, C. P., & Safko, J. L. (2002). *Classical Mechanics* (3rd ed.). Addison-Wesley.
2. Shinbrot, T., Grebogi, C., Wisdom, J., & Yorke, J. A. (1992). Chaos in a double pendulum. *American Journal of Physics*, 60(6), 491-499.
3. Hairer, E., Lubich, C., & Wanner, G. (2003). Geometric numerical integration illustrated by the Stormer-Verlet method. *Acta Numerica*, 12, 399-450.
4. Benettin, G., Galgani, L., Giorgilli, A., & Strelcyn, J.-M. (1980). Lyapunov characteristic exponents for smooth dynamical systems. *Meccanica*, 15(1), 9-20.
5. Stachowiak, T. & Okada, T. (2006). A numerical analysis of chaos in the double pendulum. *Chaos, Solitons & Fractals*, 29(2), 417-422.
6. Hairer, E., Lubich, C., & Wanner, G. (2006). *Geometric Numerical Integration* (2nd ed.). Springer.
7. Skokos, C. (2010). The Lyapunov characteristic exponents and their computation. *Lecture Notes in Physics*, 790, 63-135.
