import mujoco as mj
import numpy as np
from manipulated_object import ManipulatedObject, ObjectConfig
from dataclasses import dataclass


@dataclass(frozen=True)
class CameraConfig:
    position: tuple[int, int, int]
    rotation: np.ndarray
    resolution: tuple[int, int] = (300, 300)
    fov: int = 45
    render_depth: bool = False


class Simulator:
    def __init__(
        self,
        resolution=(500, 500),
        fovy=45,
        world_file="./data/world_mug.xml",
    ):
        self.model = mj.MjModel.from_xml_path(world_file)
        self.data = mj.MjData(self.model)

        self.model.cam_fovy = fovy
        self.model.vis.global_.fovy = fovy

        self.manipulated_object = ManipulatedObject(self.model, self.data)
        self.manipulated_object.set_orientation_euler([0, 0, 0])

        self.renderer = mj.Renderer(self.model, resolution[0], resolution[1])
        self.depth_renderer = mj.Renderer(self.model, resolution[0], resolution[1])
        self.depth_renderer.enable_depth_rendering()

    def set_object_position(self, obj_pos: list | tuple):
        obj_pos = list(obj_pos)
        self.manipulated_object.set_position(obj_pos)

    def set_object_orientation(self, orientation):
        self.manipulated_object.set_orientation_euler(orientation)

    def get_object_orientation(self) -> list[float]:
        return self.manipulated_object.get_orientation_euler()

    def get_object_config(self) -> ObjectConfig:
        return ObjectConfig.from_object(self.manipulated_object)

    def render(self, cam_rot, cam_pos):
        mj.mj_forward(self.model, self.data)
        self.data.cam_xpos = cam_pos
        self.data.cam_xmat = cam_rot.flatten()
        self.renderer.update_scene(self.data, camera=0)
        return self.renderer.render()

    def render_depth(self, cam_rot, cam_pos):
        mj.mj_forward(self.model, self.data)
        self.data.cam_xpos = cam_pos
        self.data.cam_xmat = cam_rot.flatten()
        self.depth_renderer.update_scene(self.data, camera=0)
        return self.depth_renderer.render()

    def simulate_seconds(self, seconds: float):
        seconds = max(0, seconds)
        iters = int(seconds / self.model.opt.timestep)
        for _ in range(iters):
            mj.mj_step(self.model, self.data)