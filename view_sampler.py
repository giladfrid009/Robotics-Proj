import numpy as np
from dataclasses import dataclass

from image_helpers import ImageHelpers
from simulator import Simulator
from manipulated_object import ObjectConfig


@dataclass(frozen=True)
class CameraConfig:
    position: tuple[int, int, int]
    rotation: np.ndarray
    resolution: tuple[int, int] = (300, 300)
    fov: int = 45
    render_depth: bool = False


class ViewSampler:
    def __init__(
        self,
        world_file: str,
        camera_config: CameraConfig,
        simulation_time: float = 0,
    ):
        self._simulator = Simulator(
            resolution=camera_config.resolution,
            fov=camera_config.fov,
            world_file=world_file,
        )
        self._camera_config = camera_config
        self._simulation_time = simulation_time

    @property
    def simulator(self):
        return self._simulator

    @property
    def camera_config(self) -> CameraConfig:
        return self._camera_config

    def _render_image(self):
        if self.camera_config.render_depth:
            return self.simulator.render_depth(self.camera_config.rotation, self.camera_config.position)
        return self.simulator.render(self.camera_config.rotation, self.camera_config.position)

    def get_view(self, config: ObjectConfig) -> tuple[np.ndarray, ObjectConfig]:
        self.simulator.set_object_position(config.position)
        self.simulator.set_object_orientation(config.orientation)
        self.simulator.simulate_seconds(self._simulation_time)
        image = self._render_image()
        config = self.simulator.get_object_config()
        return image, config

    def get_view_cropped(self, config: ObjectConfig, margin_factor: float = 1.2) -> tuple[np.ndarray, ObjectConfig]:
        image, config = self.get_view(config)
        mask = ImageHelpers.calc_mask(image, bg_value=0, orig_dims=False)
        x1, y1, x2, y2 = ImageHelpers.calc_bboxes(mask, margin_factor)
        cropped = image[x1:x2, y1:y2, :]
        return cropped, config