import numpy as np
import time


from utils.orient import OrientUtils
from algs.algorithm import *
from view_sampler import ViewSampler
from loss_funcs import *
import math
from tqdm.auto import tqdm


class UniformSampling(Algorithm):
    def __init__(self, test_viewer: ViewSampler, loss_func: LossFunc, num_samples: int = 1000, epoch_size: int = 50):
        super().__init__(test_viewer, loss_func)
        self.num_samples = num_samples
        self.epoch_size = epoch_size

    def solve(
        self,
        ref_img: np.ndarray,
        ref_location: tuple[float, float, float],
        run_config: RunConfig,
    ) -> tuple[ObjectPosition, RunHistory]:
        lowest_loss = np.inf
        best_orient = None

        run_start_time = time.time()
        epoch_start_time = run_start_time
        run_hist = RunHistory()

        orients = OrientUtils.generate_uniform(self.num_samples)
        np.random.default_rng(run_config.seed).shuffle(orients, axis=0)

        num_epochs = min(math.ceil(self.num_samples / self.epoch_size), run_config.max_epoch)
        for epoch in tqdm(range(num_epochs), enable=not run_config.silent):
            for test_orient in orients[epoch * self.epoch_size : (epoch + 1) * self.epoch_size]:
                loss = self.calc_loss(ref_location, ref_img, test_orient)
                if loss < lowest_loss:
                    lowest_loss = loss
                    best_orient = test_orient

            epoch_end_time = time.time()
            epoch_time = epoch_end_time - epoch_start_time
            epoch_start_time = epoch_end_time
            run_hist.add_epoch(epoch_time, lowest_loss)
            if epoch_end_time - run_start_time > run_config.max_time:
                break

        pred_position = ObjectPosition(best_orient, ref_location)
        return pred_position, run_hist


class IDUniformSampling(Algorithm):
    def __init__(self, test_viewer: ViewSampler, loss_func: LossFunc):
        super().__init__(test_viewer, loss_func)

    def solve(
        self,
        ref_img: np.ndarray,
        ref_location: tuple[float, float, float],
        run_config: RunConfig,
    ) -> tuple[ObjectPosition, RunHistory]:
        lowest_loss = np.inf
        best_orient = None

        run_start_time = time.time()
        epoch_start_time = run_start_time
        run_hist = RunHistory()

        for epoch in range(run_config.max_epoch):
            orients = OrientUtils.generate_uniform((2 + epoch) ** 3)
            for test_orient in orients:
                loss = self.calc_loss(ref_location, ref_img, test_orient)
                if loss < lowest_loss:
                    lowest_loss = loss
                    best_orient = test_orient

            epoch_end_time = time.time()
            epoch_time = epoch_end_time - epoch_start_time
            epoch_start_time = epoch_end_time
            run_hist.add_epoch(epoch_time, lowest_loss)
            if epoch_end_time - run_start_time > run_config.max_time:
                break

            pred_position = ObjectPosition(best_orient, ref_location)
            return pred_position, run_hist
