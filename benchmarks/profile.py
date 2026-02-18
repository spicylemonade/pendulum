"""Profile the simulation to identify performance bottlenecks."""
import cProfile
import pstats
import io
import numpy as np
from sim.pendulum import simulate


def run_profile():
    """Profile a 100s RK45 simulation and save top 20 functions."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    state0 = [np.pi / 4, 0.0, np.pi / 2, 0.0]

    pr = cProfile.Profile()
    pr.enable()
    simulate(state0, params, (0, 100), 0.001)
    pr.disable()

    stream = io.StringIO()
    stats = pstats.Stats(pr, stream=stream).sort_stats('cumulative')
    stats.print_stats(20)
    result = stream.getvalue()

    with open('results/profile_results.txt', 'w') as f:
        f.write(result)
        f.write('\n--- Analysis ---\n')
        f.write('The derivatives() function is called at every RK45 internal\n')
        f.write('step. For 100s of simulation, this accounts for the majority\n')
        f.write('of runtime. Potential optimizations:\n')
        f.write('- Numba JIT compilation of derivatives() (see numba.pydata.org)\n')
        f.write('- Vectorized batch evaluation using numpy\n')
        f.write('- C extension via Cython for inner loop\n')

    print(result[:2000])
    print('Profile saved to results/profile_results.txt')


if __name__ == '__main__':
    run_profile()
