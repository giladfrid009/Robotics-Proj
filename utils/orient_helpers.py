import numpy as np
import math
from scipy.spatial.transform import Rotation


class OrientUtils:

    LOWER_BOUND = np.asanyarray([-np.pi, -np.pi / 2, -np.pi])
    UPPER_BOUND = np.asanyarray([np.pi, np.pi / 2, np.pi])

    @staticmethod
    def _uniform_det_axes(num_pts: int) -> np.ndarray:
        indices = np.arange(0, num_pts, dtype=float) + 0.5
        phi = np.arccos(1 - 2 * indices / num_pts)
        theta = np.pi * (1 + 5**0.5) * indices
        x, y, z = np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)
        xyz = np.stack((x, y, z), axis=-1)
        return xyz

    @staticmethod
    def _uniform_rnd_axes(num_pts: int, rng: np.random.Generator) -> np.ndarray:
        xyz = rng.normal(size=(num_pts, 3))
        xyz = xyz / np.linalg.norm(xyz, axis=1)[:, np.newaxis]
        return xyz

    @staticmethod
    def generate_uniform(min_samples: int):
        n = math.ceil(math.pow(min_samples, 1 / 3))
        axes = OrientUtils._uniform_det_axes(n**2)
        axes = np.repeat(axes, n, axis=0)
        rots = np.linspace(0, 2 * np.pi, num=n, endpoint=False)
        rots = np.tile(rots, n**2)
        rot_vec = np.expand_dims(rots, axis=-1) * axes
        orients = Rotation.from_rotvec(rot_vec).as_euler("xyz")
        return orients

    @staticmethod
    def generate_random(num_samples: int, rnd_seed: int = None):
        n = math.ceil(math.pow(num_samples, 1 / 3))
        rng = np.random.default_rng(rnd_seed)
        axes = OrientUtils._uniform_rnd_axes(n**2, rng)
        axes = np.repeat(axes, n, axis=0)
        rots = rng.uniform(0, 2 * np.pi, size=n**3)
        rot_vec = np.expand_dims(rots, axis=-1) * axes
        orients = Rotation.from_rotvec(rot_vec).as_euler("xyz")
        return orients