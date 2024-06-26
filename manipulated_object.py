from dataclasses import dataclass
from scipy.spatial.transform import Rotation


class ManipulatedObject:
    """
    represent, query and manually manipulate the manipulated object
    assuming it's body name is 'manipulated_object'
    """

    def __init__(self, mj_model, mj_data):
        self._model = mj_model
        self._data = mj_data
        self._jntadr = mj_model.body("manipulated_object").jntadr[0]

    def set_location(self, location: tuple[float, float, float]):
        assert len(location) == 3
        self._data.qpos[self._jntadr : self._jntadr + 3] = location

    def set_orientation(self, orient: tuple[float, float, float]):
        assert len(orient) == 3
        orient_quat = Rotation.from_euler("xyz", orient, degrees=False).as_quat()
        self._data.qpos[self._jntadr + 3 : self._jntadr + 7] = orient_quat

    def get_orientation(self) -> tuple[float, float, float]:
        quat = self._data.qpos[self._jntadr + 3 : self._jntadr + 7]
        rotation = Rotation.from_quat(quat).as_euler("xyz", degrees=False)
        return rotation

    def get_location(self) -> tuple[float, float, float]:
        return self._data.qpos[self._jntadr : self._jntadr + 3]


@dataclass(frozen=True)
class ObjectPosition:
    orientation: tuple[float, float, float]
    location: tuple[float, float, float]

    @staticmethod
    def from_object(obj_state: ManipulatedObject):
        return ObjectPosition(obj_state.get_orientation(), obj_state.get_location())
