import os
from eval.eval_log import EvalLog
import pandas as pd


class Files:
    def __init__(
        self,
        directory: str,
        extension: str = "",
        scan_dirs: bool = False,
        return_full_path: bool = True,
    ) -> None:
        self.root = directory
        self.extension = extension
        self.scan_dirs: bool = scan_dirs
        self.return_full_path = return_full_path
        self.results: list[os.DirEntry] = []

        self._pos = -1

        self._scan()

    def _scan(self):
        self.results: list = []
        self._pos = -1

        for result in os.scandir(self.root):
            if self.scan_dirs and result.is_dir():
                self.results.append(result)
            else:
                if result.name.endswith(self.extension):
                    self.results.append(result)

        self.results = sorted(self.results, key=lambda f: f.name)

    def __getitem__(self, index: int) -> os.DirEntry:
        return self.results[index]

    def __iter__(self):
        self._pos = -1
        return self

    def __next__(self):
        self._pos += 1
        if self._pos >= self.__len__():
            raise StopIteration

        result: os.DirEntry = self.results[self._pos]
        if self.return_full_path:
            return result.path
        return result.name

    def __len__(self) -> int:
        return len(self.results)

    def get_filename(self) -> str:
        return self.results[self._pos].name

    def get_path(self) -> str:
        return self.results[self._pos].path

    def seek(self, pos: int):
        if 0 <= pos < self.__len__():
            self._pos = pos - 1
            return self.__next__()


class LogFiles(Files):
    def __init__(
        self,
        directory: str,
        extension: str = ".pickle",
        scan_dirs: bool = False,
        return_full_path: bool = True,
    ) -> None:
        super().__init__(directory, extension, scan_dirs, return_full_path)

    def _load(self) -> EvalLog:
        return EvalLog.load(self.get_path())

    def to_dataframe(self, add_params: bool = False) -> pd.DataFrame:
        log = self._load()
        return log.to_dataframe(add_params)
