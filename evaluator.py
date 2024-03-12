from tqdm.auto import tqdm
import numpy as np

from image_helpers import ImageHelpers
from view_sampler import ViewSampler
from eval_funcs import EvalFunc
from manipulated_object import ObjectConfig
from algs.algorithm import Algorithm, SearchConfig


class Evaluator:
    def __init__(self, world_viewer: ViewSampler, eval_func: EvalFunc) -> None:
        self.world_viewer = world_viewer
        self.eval_func = eval_func

    def evaluate(self, alg: Algorithm, alg_config: SearchConfig, init_configs: list[ObjectConfig]) -> list[float]:
        losses = []

        print(f"Evaluating Algorithm: {type(alg).__name__} | Config: {alg_config}")

        for init_config in tqdm(init_configs, desc=f"Evaluating: "):

            ref_img, ref_config = self.world_viewer.get_view_cropped(init_config, depth=False)

            pred_orient = alg.find_orientation(ref_img, ref_config.position, alg_config)

            ref_depth, _ = self.world_viewer.get_view_cropped(
                config=ref_config,
                depth=True,
                allow_simulation=False,
            )

            test_depth, _ = self.world_viewer.get_view_cropped(
                config=ObjectConfig(pred_orient, ref_config.position),
                depth=True,
                allow_simulation=False,
            )

            pad_shape = np.maximum(ref_depth.shape, test_depth.shape)
            ref_depth = ImageHelpers.pad_to_shape(ref_depth, pad_shape, pad_value=100)
            test_depth = ImageHelpers.pad_to_shape(test_depth, pad_shape, pad_value=100)

            loss = self.eval_func(ref_depth, test_depth)
            losses.append(loss)

        return losses