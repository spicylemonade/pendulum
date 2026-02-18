# Equations of Motion for the Double Pendulum

## System Description

Consider two point masses m₁ and m₂ connected by rigid massless rods of lengths l₁ and l₂. The first rod is attached to a fixed pivot; the second rod is attached to m₁. The generalized coordinates are the angles θ₁ and θ₂ measured from the vertical (downward) direction. See [goldstein2002classical] and [wikipedia_double_pendulum] for standard treatments.

## Cartesian Coordinates

The positions of the two masses in Cartesian coordinates (origin at pivot, y-axis pointing down):

- x₁ = l₁ sin θ₁,  y₁ = -l₁ cos θ₁
- x₂ = l₁ sin θ₁ + l₂ sin θ₂,  y₂ = -l₁ cos θ₁ - l₂ cos θ₂

## Kinetic Energy

The velocities are obtained by differentiating:

- v₁² = l₁² θ̇₁²
- v₂² = l₁² θ̇₁² + l₂² θ̇₂² + 2 l₁ l₂ θ̇₁ θ̇₂ cos(θ₁ - θ₂)

The total kinetic energy is:

**T = ½(m₁ + m₂) l₁² θ̇₁² + ½ m₂ l₂² θ̇₂² + m₂ l₁ l₂ θ̇₁ θ̇₂ cos(θ₁ - θ₂)**

## Potential Energy

Taking the pivot as the reference level:

**V = -(m₁ + m₂) g l₁ cos θ₁ - m₂ g l₂ cos θ₂**

## The Lagrangian

**L = T - V = ½(m₁ + m₂) l₁² θ̇₁² + ½ m₂ l₂² θ̇₂² + m₂ l₁ l₂ θ̇₁ θ̇₂ cos(θ₁ - θ₂) + (m₁ + m₂) g l₁ cos θ₁ + m₂ g l₂ cos θ₂**

## Euler-Lagrange Equations

Applying d/dt(∂L/∂θ̇ᵢ) - ∂L/∂θᵢ = 0 for i = 1, 2, we obtain two coupled second-order ODEs. Defining Δθ = θ₁ - θ₂ for brevity:

### Equation 1 (for θ₁):

**(m₁ + m₂) l₁ θ̈₁ + m₂ l₂ θ̈₂ cos Δθ + m₂ l₂ θ̇₂² sin Δθ + (m₁ + m₂) g sin θ₁ = 0**

### Equation 2 (for θ₂):

**m₂ l₂ θ̈₂ + m₂ l₁ θ̈₁ cos Δθ - m₂ l₁ θ̇₁² sin Δθ + m₂ g sin θ₂ = 0**

## Solving for the Angular Accelerations

The two equations form a linear system in (θ̈₁, θ̈₂). Solving:

Let Δθ = θ₁ - θ₂, M = m₁ + m₂, and den = M l₁ - m₂ l₁ cos²Δθ. Then:

**θ̈₁ = [-m₂ l₂ θ̇₂² sin Δθ - M g sin θ₁ + m₂ (l₁ θ̇₁² sin Δθ - g sin θ₂) cos Δθ] / (l₁ den)**

The denominator for the full system (from the 2×2 matrix inversion) is:

**D = l₁ l₂ (M - m₂ cos²Δθ)**

Explicitly:

**θ̈₁ = [-m₂ l₂ θ̇₂² sin Δθ cos Δθ + m₂ l₁ θ̇₁² sin Δθ cos²Δθ - M g sin θ₁ ... ] / ...**

Rather than writing the full expanded form, the standard approach is to solve the 2×2 linear system numerically at each time step. Dividing out m₂ from equation 2:

- Eq1: M l₁ θ̈₁ + m₂ l₂ cos Δθ θ̈₂ = -m₂ l₂ θ̇₂² sin Δθ - M g sin θ₁
- Eq2: l₁ cos Δθ θ̈₁ + l₂ θ̈₂ = l₁ θ̇₁² sin Δθ - g sin θ₂

Solving via Cramer's rule with D = M l₁ l₂ - m₂ l₁ l₂ cos²Δθ:

**θ̈₁ = [(-m₂ l₂ θ̇₂² sin Δθ - M g sin θ₁) l₂ - (l₁ θ̇₁² sin Δθ - g sin θ₂) m₂ l₂ cos Δθ] / D**

**θ̈₂ = [(l₁ θ̇₁² sin Δθ - g sin θ₂) M l₁ - (-m₂ l₂ θ̇₂² sin Δθ - M g sin θ₁) l₁ cos Δθ] / D**

Simplified (see [landau1976mechanics], [scipython_double_pendulum]):

**θ̈₁ = [-m₂ l₁ θ̇₁² sin(2Δθ)/2 - m₂ l₂ θ̇₂² sin Δθ - (M g sin θ₁ - m₂ g sin θ₂ cos Δθ)] / [l₁(M - m₂ cos²Δθ)]**

**θ̈₂ = [M l₁ θ̇₁² sin Δθ + m₂ l₂ θ̇₂² sin(2Δθ)/2 + M g sin θ₁ cos Δθ - M g sin θ₂] / [l₂(M - m₂ cos²Δθ)]**

## Reduction to First-Order ODE System

Defining the state vector **y** = [θ₁, ω₁, θ₂, ω₂] where ω₁ = θ̇₁ and ω₂ = θ̇₂:

- dy₁/dt = ω₁
- dy₂/dt = θ̈₁(θ₁, ω₁, θ₂, ω₂)  (from equation above)
- dy₃/dt = ω₂
- dy₄/dt = θ̈₂(θ₁, ω₁, θ₂, ω₂)  (from equation above)

This system of four first-order ODEs is suitable for numerical integration using RK45 [hairer2006geometric] or symplectic methods [hairer2003geometric].

## Total Energy (for Verification)

The total energy H = T + V is conserved for the undamped system:

**H = ½(m₁ + m₂) l₁² ω₁² + ½ m₂ l₂² ω₂² + m₂ l₁ l₂ ω₁ ω₂ cos(θ₁ - θ₂) - (m₁ + m₂) g l₁ cos θ₁ - m₂ g l₂ cos θ₂**

## References

- [goldstein2002classical] Goldstein, Poole, Safko. *Classical Mechanics*, 3rd ed., 2002.
- [landau1976mechanics] Landau, Lifshitz. *Mechanics*, 3rd ed., 1976.
- [wikipedia_double_pendulum] Wikipedia. *Double pendulum*.
- [scipython_double_pendulum] SciPython. *The Double Pendulum*.
- [hairer2003geometric] Hairer, Lubich, Wanner. *Geometric numerical integration illustrated by the Stormer-Verlet method*, Acta Numerica, 2003.
- [hairer2006geometric] Hairer, Lubich, Wanner. *Geometric Numerical Integration*, Springer, 2006.
