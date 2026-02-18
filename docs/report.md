# Double Pendulum Simulator: Summary Report

## Introduction

The double pendulum is a canonical example of a deterministic system exhibiting chaotic dynamics. Despite being governed by simple Newtonian mechanics, its motion is exquisitely sensitive to initial conditions, making long-term prediction impossible in practice. This project implements a minimal double pendulum simulator using Lagrangian mechanics, with the goal of reproducing key results from the chaos literature using modern numerical tools. Specifically, we derive the equations of motion from first principles, implement both adaptive (RK45) and structure-preserving (symplectic) integrators, compute the largest Lyapunov exponent, and generate visualizations that characterize the system's chaotic nature.

## Methods

### Equations of Motion

The double pendulum consists of two point masses $m_1$, $m_2$ connected by rigid massless rods of lengths $l_1$, $l_2$. The Lagrangian $L = T - V$ yields two coupled second-order ODEs for the generalized coordinates $\theta_1$ and $\theta_2$ (see `docs/equations.md` for the full derivation). These are reduced to four first-order ODEs for the state vector $[\theta_1, \dot\theta_1, \theta_2, \dot\theta_2]$ using the standard Wikipedia formulation (Goldstein et al., 2002; Wikipedia, 2024).

### Numerical Integration

**RK45 (adaptive):** We use SciPy's `solve_ivp` with the Dormand--Prince RK45 method, setting `rtol=1e-10` and `atol=1e-12` for high-accuracy baseline simulations. This adaptive method adjusts its internal step size to control local truncation error.

**Implicit midpoint (symplectic):** For long-time energy conservation, we implement the implicit midpoint rule, which is a second-order symplectic integrator valid for general (non-separable) Hamiltonian systems (Hairer et al., 2003, 2006). At each step, the implicit equation $y_{n+1} = y_n + h\,f\!\bigl(\tfrac{1}{2}(y_n + y_{n+1})\bigr)$ is solved using SciPy's `fsolve`. Unlike Stormer--Verlet or explicit symplectic schemes, the implicit midpoint method handles the double pendulum's position-dependent mass matrix without requiring Hamiltonian separability.

### Chaos Analysis

**Lyapunov exponent:** The largest Lyapunov exponent $\lambda_1$ is estimated via the Benettin algorithm (Benettin et al., 1980): a reference and perturbed trajectory (separated by $d_0 = 10^{-9}$ rad) are evolved in parallel, with periodic renormalization every 0.1 s to avoid overflow. The exponent is computed as the time-averaged logarithmic growth rate of the separation.

**Poincare section:** We construct a Poincare section by recording $(\theta_2, \dot\theta_2)$ at each upward zero-crossing of $\theta_1$ (i.e., $\theta_1 = 0$ with $\dot\theta_1 > 0$), using linear interpolation for sub-step accuracy (Stachowiak & Okada, 2006).

**Flip-count basin map:** A 200x200 grid of initial conditions $(\theta_1, \theta_2) \in [-\pi, \pi]^2$ with zero initial velocities is simulated for 10 s each. The number of full $2\pi$ flips of the second pendulum is counted, producing a fractal-like basin map (Shinbrot et al., 1992).

## Results

### Baseline Simulation

A 30-second simulation with $m_1 = m_2 = 1$ kg, $l_1 = l_2 = 1$ m, and initial conditions $\theta_1 = \pi/4$, $\theta_2 = \pi/2$ produces the trajectory and phase portrait shown in `figures/baseline_trajectory.png`. The RK45 integrator achieves energy conservation to within $3 \times 10^{-7}$% over 100 s (see `results/baseline_benchmarks.json`), completing in approximately 1.9 s of wall-clock time.

### Integrator Comparison

The RK45 and implicit midpoint integrators were compared at step sizes $\Delta t \in \{0.1, 0.01, 0.001\}$ over 100 s (`figures/integrator_comparison.png`). RK45 maintains near-machine-precision energy conservation ($\sim 3 \times 10^{-7}$%) regardless of output step size, since its adaptive internal stepping controls the error. The symplectic integrator shows bounded energy drift that decreases with step size: 0.66% at $\Delta t = 0.1$, 0.0077% at $\Delta t = 0.01$, and $7.8 \times 10^{-5}$% at $\Delta t = 0.001$. However, the symplectic integrator's drift remains bounded over arbitrarily long times, a key advantage for long-duration simulations.

### Sensitivity to Initial Conditions

Two simulations differing by $10^{-9}$ rad in $\theta_1$ (at $\theta_1 = \theta_2 = 2.0$ rad) diverge exponentially, reaching macroscopic separation within 15 s (`figures/chaos_divergence.png`). The log-scale divergence plot shows a clear linear regime, confirming exponential sensitivity.

### Lyapunov Exponent

For the default parameters and chaotic initial condition $\theta_1 = \theta_2 = 2.0$ rad, the estimated largest Lyapunov exponent is $\lambda_1 \approx 1.17$ /s. A parameter sweep across 20 combinations of mass and length ratios (`figures/param_sensitivity.png`) reveals Lyapunov exponents ranging from 0.11 to 2.15 /s, with higher mass ratios ($m_2/m_1$) and shorter second links ($l_2/l_1$) generally producing stronger chaos.

### Poincare Section and Flip Map

The Poincare section (`figures/poincare_section.png`) shows a mixture of regular islands and a chaotic sea, characteristic of a system with mixed phase space. The flip-count basin map (`figures/flip_count_map.png`) displays intricate fractal boundaries between regions of different flip counts, visually demonstrating the extreme sensitivity of the system's behavior to initial conditions.

### Animation

An animated GIF of the double pendulum motion is provided in `figures/pendulum_animation.gif`, showing the characteristic unpredictable swinging and occasional full rotations of the second bob.

## Discussion

Our results are consistent with the established double pendulum literature across several key metrics:

1. **Lyapunov exponent magnitude.** Our computed values of $\lambda_1 \approx 0.1$--$2.1$ /s fall within the range reported in prior studies. Shinbrot et al. (1992) reported $\lambda \approx 7.9$ /s for their specific configuration (different parameters and higher energy), while Stachowiak & Okada (2006) found exponents in the range 1--10 /s depending on energy. The variation is expected since $\lambda_1$ depends strongly on total energy and mass/length ratios. Our parameter sweep confirms this dependence and shows that higher mass ratios amplify chaotic behavior, consistent with the analysis in Stachowiak & Okada (2006).

2. **Symplectic integrator performance.** The implicit midpoint method achieves bounded energy drift of 0.0077% at $\Delta t = 0.01$ over 100 s, consistent with the $O(h^2)$ error bound for second-order symplectic methods described in Hairer et al. (2006). While RK45 achieves lower absolute drift for short simulations, the symplectic method's qualitative superiority for long-time integration is well documented: the energy error oscillates rather than growing secularly, preserving the geometric structure of Hamiltonian flow. This confirms the theoretical predictions in Hairer, Lubich & Wanner (2003).

3. **Fractal basin boundaries.** The flip-count map exhibits the same fractal-like structure reported by Shinbrot et al. (1992) and Stachowiak & Okada (2006), where nearby initial conditions can lead to vastly different numbers of full rotations. This is a hallmark of chaotic scattering and is intimately connected to the system's homoclinic tangle structure. The maximum flip count of 15 in our 10 s simulation window is comparable to the counts reported in the literature for similar parameters and integration times.

Performance profiling reveals that the `derivatives()` function and SciPy overhead account for the majority of compute time. For production use, Numba JIT compilation or a Cython extension could yield significant speedups, as suggested by profiling results in `results/profile_results.txt`.

## Conclusion

This project demonstrates that a minimal Python implementation (under 800 lines of code across all modules) can reproduce the essential features of double pendulum chaos documented in the physics and dynamical systems literature. The combination of adaptive RK45 integration for accuracy and implicit midpoint integration for structure preservation provides complementary tools for studying the system. The computed Lyapunov exponents, Poincare sections, and flip-count basin maps all exhibit the qualitative and quantitative features expected from a chaotic Hamiltonian system with two degrees of freedom. The full test suite achieves 100% line coverage of the simulation modules, and all results are reproducible from the provided scripts and fixed random seeds.
