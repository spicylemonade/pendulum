# Project Scope: Minimal Double Pendulum Simulator

## Scope Statement

Build a minimal double pendulum simulator using Lagrangian mechanics with real-time visualization.

## Repository Structure

### Existing Files
| File | Purpose |
|------|---------|
| `README.md` | Project overview (stub) |
| `.gitignore` | Git ignore rules for secrets, env files, logs |
| `.gitattributes` | Git LFS and attribute configuration |
| `research_rubric.json` | Research task tracking rubric |
| `sources.bib` | BibTeX bibliography for all references |

### Project Directories
| Directory | Purpose |
|-----------|---------|
| `sim/` | Core simulation code (equations of motion, integration, visualization) |
| `tests/` | Pytest test suite for correctness validation |
| `experiments/` | Scripts for chaos analysis, parameter sweeps, comparisons |
| `benchmarks/` | Performance timing and profiling scripts |
| `results/` | JSON output files from experiments and benchmarks |
| `figures/` | Publication-quality PNG/PDF plots and animations |
| `docs/` | Documentation: equations, survey, scope, report |

### Configuration
| Config | Purpose |
|--------|---------|
| `.gitignore` | Prevents committing secrets (.env, .key, .pem), IDE files, and agent logs |
| `.gitattributes` | Configures Git LFS tracking for large binary files |

## Project Scope Details

### In Scope
- Lagrangian derivation of double pendulum equations of motion
- RK45 numerical integration via SciPy `solve_ivp`
- Symplectic (Stormer-Verlet) integration for energy conservation
- Energy conservation verification
- Static trajectory plots and phase portraits
- Animated GIF visualization of pendulum motion
- Chaos characterization: sensitivity to initial conditions, Lyapunov exponents
- Poincare section analysis
- Flip-count basin maps
- Parameter sensitivity studies (mass/length ratios)
- Performance benchmarking and profiling

### Out of Scope
- Real-time interactive GUI (beyond matplotlib animation)
- 3D visualization
- Triple or N-pendulum extensions
- Machine learning or neural network approaches
- Web-based deployment

### Design Constraints
- Python only, using NumPy/SciPy/Matplotlib
- Total Python LOC < 800 across all source directories
- No single file exceeds 150 lines
- Fixed random seed (42) for reproducibility
- All figures publication-quality (Nature/Science standard)
