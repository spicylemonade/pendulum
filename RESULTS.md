# Results and Analysis

## 1. Chaos Characterization (Item 022)

### Maximum Lyapunov Exponent

We computed the maximum Lyapunov exponent (MLE) using the standard two-trajectory method with periodic renormalization (d0=1e-9, renormalization every 0.5s, total integration 500s).

**Result**: MLE = 0.978 s^-1

This positive value confirms that the double pendulum with our canonical initial conditions (theta1=theta2=pi/2, omega1=omega2=0, equal unit masses and lengths) exhibits chaotic dynamics.

**Comparison with Shinbrot et al. (1992)**: The foundational experimental work reported lambda = 7.5 +/- 1.5 s^-1 and numerical simulations gave lambda = 7.9 +/- 0.4 s^-1 (Table 1 of their paper). However, their experiments used different physical parameters and released the pendulum from near-vertical positions at significantly higher energy. The MLE is strongly energy-dependent: at low energies the system is integrable (MLE = 0), and it grows with energy as more of the phase space becomes chaotic. Our initial conditions have E = 0 J (the zero of potential energy at horizontal), while Shinbrot et al.'s configuration had much higher total energy. The factor-of-8 difference in MLE is therefore expected and consistent with the energy-dependent transition documented in Stachowiak & Okada (2006, Section 3, Figures 3-5).

### Poincare Section

The Poincare section was computed at energy E = -10 J using the surface theta2 = 0 with omega2 > 0. We sampled 15 initial conditions on this energy surface and collected 3430 total crossings.

The resulting section shows a mixture of regular orbits (appearing as closed curves or island chains) and chaotic regions (appearing as scattered points filling an area), which is the hallmark of a mixed phase space at moderate energies. This structure is qualitatively consistent with:
- Stachowiak & Okada (2006), Figures 3-5, which show the transition from regular to chaotic structure as energy increases
- Jimenez Lopez & Garcia Garrido (2024), who used Lagrangian descriptors to characterize the same regular/chaotic boundary

### Flip-Count Map

The 100x100 flip-count map (theta1, theta2 in [-pi, pi], omega1=omega2=0, T=10s) reveals fractal boundary structures between regions of different flip counts. The central region near (0,0) shows no flips (energetically impossible when 3*cos(theta1) + cos(theta2) > 2, as noted by Heyl). The fractal boundaries are consistent with:
- Heyl's "Double Pendulum Fractal" analysis, which identifies the energetic boundary for flipping
- Liang et al. (2024), who developed algorithms for computing fractal basins of attraction and uncovered "petal-like structures characterized by significant rotational symmetry and fractal features"

### Parameter Sweeps

**Mass ratio (m2/m1)**: The MLE varies non-monotonically across mass ratios 0.1-10, ranging from 0.05 to 0.95 s^-1. All values are positive, confirming chaos persists across the entire range. Jimenez Lopez & Garcia Garrido (2024) found that for a given mass ratio, the maximum chaotic fraction is attained when the pendulums have equal lengths. Our results are consistent with this: the MLE sensitivity to mass ratio is less pronounced than to energy.

**Length ratio (L2/L1)**: The chaotic fraction (measured by flip occurrence on a 30x30 grid) ranges from 0.64 to 0.81 across length ratios 0.1-10. While Jimenez Lopez & Garcia Garrido (2024) found maximum chaos at equal lengths, our metric (flip fraction rather than Lagrangian descriptor) shows a more complex dependence, with higher chaotic fractions at short L2. This may reflect the different energy landscape when L2 is short: the second pendulum can flip more easily when its moment of inertia is small.

## 2. Integrator Comparison (Item 023)

### Convergence Order

The convergence study (5 time steps from dt=0.01 to dt=0.0005) confirms:
- **RK4**: Measured convergence slope = **4.02** on a log-log plot of state error vs dt, consistent with the theoretical 4th-order accuracy. This is the classical result for the 4th-order Runge-Kutta method.
- **Implicit midpoint**: Measured slope = **2.00**, consistent with its theoretical 2nd-order accuracy. The implicit midpoint method is the simplest symplectic integrator applicable to general (non-separable) Hamiltonian systems (Hairer, Lubich & Wanner, 2006, Chapter VI).

### Long-Term Energy Behavior

At dt=0.01 (coarse):
- RK4 energy drift: 6.03e-05 (small but secular — the drift accumulates over time)
- Implicit midpoint: 2.00e-03 (larger per-step but bounded oscillation)

At dt=0.001 (fine):
- RK4: 1.31e-09 (negligible)
- Implicit midpoint: 2.71e-05 (still bounded)

The key distinction is the *qualitative* behavior: RK4's energy error grows secularly (approximately as t * dt^4), while the symplectic integrator's error oscillates around zero. This is a consequence of the backward error analysis: symplectic integrators exactly solve a nearby Hamiltonian, so energy is preserved up to an O(dt^2) modification (Hairer, Lubich & Wanner, 2006, Theorem IX.8.1).

### Trade-offs and Recommendations

| Task | Recommended Integrator | Reason |
|------|----------------------|--------|
| Short, accurate trajectories (t < 10s) | RK4 | Much higher per-step accuracy (O(dt^4) vs O(dt^2)) |
| Long-term statistical properties | Implicit midpoint | Bounded energy error preserves phase space structure |
| Poincare sections | RK4 (small dt) | Need accurate crossing detection |
| Lyapunov exponents | RK4 | Short segments between renormalizations |
| Flip-count maps | RK4 (moderate dt) | Speed matters more than long-term stability |

For the double pendulum specifically, the non-separable Hamiltonian means the standard Stormer-Verlet / leapfrog method cannot be applied directly. The implicit midpoint method is the standard choice for such systems (Hairer, Lubich & Wanner, 2006, Section II.1.3), though it requires solving an implicit equation at each step via fixed-point iteration, making it roughly 2x slower than RK4 (measured: 2.10s vs 1.28s for the same simulation).
