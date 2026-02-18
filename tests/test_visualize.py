"""Tests for sim/visualize.py: plot generation."""
import os
import numpy as np
from sim.pendulum import simulate
from sim.visualize import plot_trajectories, animate_pendulum


def test_plot_trajectories_creates_file(tmp_path):
    """plot_trajectories creates a PNG file."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    result = simulate([0.5, 0, 0.5, 0], params, (0, 2), 0.01)
    path = str(tmp_path / 'test_traj')
    plot_trajectories(result, savepath=path)
    assert os.path.exists(path + '.png')


def test_animate_pendulum_creates_gif(tmp_path):
    """animate_pendulum creates a GIF file."""
    params = {'m1': 1.0, 'm2': 1.0, 'l1': 1.0, 'l2': 1.0, 'g': 9.81}
    result = simulate([0.5, 0, 0.5, 0], params, (0, 1), 0.01)
    path = str(tmp_path / 'test_anim.gif')
    animate_pendulum(result, params, savepath=path, skip=5)
    assert os.path.exists(path)
