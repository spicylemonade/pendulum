# Double Pendulum Simulator: Chaos, Lyapunov Exponents, and Fractal Structure

A minimal but comprehensive double pendulum simulation exploring chaotic dynamics through numerical integration, Lyapunov exponent computation, Poincare sections, and fractal flip-count maps. This project implements the equations of motion from the Lagrangian formulation and compares RK4 with a symplectic (implicit midpoint) integrator.

## Mathematical Background

The double pendulum consists of two point masses *m*_1, *m*_2 connected by rigid massless rods of lengths *L*_1, *L*_2. The first rod pivots at a fixed point, and both swing freely under gravity *g* in the vertical plane.

### Generalized Coordinates

- theta_1: angle of the first rod from the downward vertical
- theta_2: angle of the second rod from the downward vertical

### Lagrangian

The kinetic and potential energies are:

    T = (1/2)(m1+m2) L1^2 w1^2 + (1/2) m2 L2^2 w2^2 + m2 L1 L2 w1 w2 cos(theta1-theta2)
    V = -(m1+m2) g L1 cos(theta1) - m2 g L2 cos(theta2)

where w1 = dtheta1/dt, w2 = dtheta2/dt.

### Equations of Motion

Applying the Euler-Lagrange equations and solving the resulting coupled system for the angular accelerations yields a system of four first-order ODEs:

    dtheta1/dt = omega1
    domega1/dt = f1(theta1, omega1, theta2, omega2; m1, m2, L1, L2, g)
    dtheta2/dt = omega2
    domega2/dt = f2(theta1, omega1, theta2, omega2; m1, m2, L1, L2, g)

The explicit expressions for f1 and f2 are implemented in `pendulum.py:derivatives()`, following the standard formulation from the Wikipedia double pendulum article and Shinbrot et al. (1992).

## Installation

### Dependencies

    pip install numpy matplotlib scipy seaborn

Or use the provided requirements file:

    pip install -r requirements.txt

### Python Version

Python 3.8 or later is required. All computations use NumPy arrays for efficiency.

## Usage

### Run the baseline simulation (30 seconds)

    python run_baseline.py

Produces: trajectory data in `results/`, four figures in `figures/` (angular displacement, tip trajectory, phase portraits, energy drift).

### Run chaos analysis (sensitivity, Lyapunov, Poincare, symplectic comparison)

    python run_phase3.py

Produces: sensitivity to initial conditions plots, Lyapunov exponent convergence, Poincare section, integrator energy comparison.

### Generate the flip-count map

    python run_flipmap.py

Produces: 100x100 flip-count heatmap in `figures/flip_count_map.png`.

### Run experiments (convergence, parameter sweeps, benchmarks, validation)

    python run_phase4.py

Produces: convergence study, mass ratio and length ratio parameter sweeps, performance benchmarks, scipy validation.

## Key Results

### Energy Conservation

With RK4 at dt=0.001 over 30 seconds, the maximum relative energy drift is **1.31e-09** (normalized by the system's energy scale of 29.43 J). This is well below the 1e-4 threshold, confirming excellent energy conservation.

### Maximum Lyapunov Exponent

The computed MLE is **0.978 s^-1** for the canonical initial conditions (theta1=theta2=pi/2, omega1=omega2=0). This positive value confirms chaotic dynamics. The value is within the expected order of magnitude: Shinbrot et al. (1992) measured lambda = 7.5 +/- 1.5 s^-1 experimentally and 7.9 +/- 0.4 s^-1 numerically, but at significantly higher energy (their pendulum was released from near-vertical positions with different parameters). Our lower-energy initial conditions produce a correspondingly lower MLE, consistent with the energy-dependent chaos transition documented in Stachowiak & Okada (2006).

### Poincare Section

The Poincare section (surface: theta2=0, omega2>0) at E=-10 J shows a mixture of regular and chaotic regions, with 3430 crossings from 15 initial conditions. The structure is qualitatively consistent with the sections published in Stachowiak & Okada (2006) and the interactive tool by Stein (2020).

### Flip-Count Map

The 100x100 flip-count map reveals the characteristic fractal boundary structure between regions of different flip counts, with a maximum of 15 flips observed in the 10-second simulation window. The fractal basin boundaries are consistent with the structures described by Heyl and the 2024 study by Liang et al.

### Integrator Comparison

- **RK4**: 4th-order convergence (measured slope = 4.02). Excellent per-step accuracy but energy drifts secularly at large time steps.
- **Implicit midpoint (symplectic)**: 2nd-order convergence (slope = 2.00). Lower per-step accuracy but energy oscillates around the true value without secular drift, as predicted by backward error analysis (Hairer, Lubich & Wanner, 2006).

### Parameter Sweeps

- **Mass ratio sweep**: MLE varies non-monotonically between 0.05 and 0.95 s^-1 across mass ratios 0.1-10.
- **Length ratio sweep**: Chaotic fraction (measured by flip occurrence) ranges 0.64-0.81, with higher values at shorter L2 relative to L1.

### Scipy Validation

Custom RK4 (dt=0.001) agrees with scipy DOP853 (rtol=atol=1e-12) to **10.1 significant figures** at t=1s, **9.5 significant figures** at t=10s, and diverges completely by t=30s as expected for a chaotic system.

## Project Structure

    pendulum.py          - Core simulation module (equations, integrators, energy)
    run_baseline.py      - Baseline simulation and visualization
    run_phase3.py        - Chaos analysis experiments
    run_flipmap.py       - Flip-count map generation
    run_phase4.py        - Convergence, sweeps, benchmarks, validation
    sources.bib          - Bibliography (17 BibTeX entries)
    research_rubric.json - Research plan and progress tracking
    results/             - Experimental data (JSON, NPZ)
    figures/             - Publication-quality plots (PNG 300dpi + PDF)

## References

1. Shinbrot, T., Grebogi, C., Wisdom, J., & Yorke, J. A. (1992). Chaos in a double pendulum. *American Journal of Physics*, 60(6), 491-499.
2. Stachowiak, T., & Okada, T. (2006). A numerical analysis of chaos in the double pendulum. *Chaos, Solitons & Fractals*, 29(2), 417-422.
3. Jimenez Lopez, J., & Garcia-Garrido, V. J. (2024). Chaos and regularity in the double pendulum with Lagrangian descriptors. *International Journal of Bifurcation and Chaos*, 34(16), 2450201.
4. Hairer, E., Lubich, C., & Wanner, G. (2006). *Geometric Numerical Integration* (2nd ed.). Springer.
5. Contreras, J. C., Generelo-Rico, G., & Palomares-Ruiz, J. E. (2024). Deterministic chaos: A pedagogical review of the double pendulum case. *Revista Brasileira de Ensino de Fisica*, 46.
6. D'Alessio, S. (2023). The double pendulum: a numerical study with the Euler and RK4 methods. *European Journal of Physics*, 44(1), 015002.
7. Liang, J. et al. (2024). A novel global perspective: Characterizing the fractal basins of attraction and the level of chaos in a double pendulum. *Chaos, Solitons & Fractals*, 189, 115694.

See `sources.bib` for the complete bibliography.
