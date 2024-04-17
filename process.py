from simpy import Environment
from store import Store

from typing import Callable, Union, TypeVar, Generic

PeriodSampler = Union[int, float, Callable[None, Union[float, int]]]
T = TypeVar("T")
U = TypeVar("U")


class GenericProcess:
    def __init__(
        self,
        env: Environment,
        store_from: Store,
        store_to: Store,
        store_builder: Callable[T, U],
        period: PeriodSampler,
    ):
        self._env = env
        self._from = store_from
        self._to = store_to
        self._store_builder = store_builder
        self._period = period

    def _sample_period(self) -> float:
        if isinstance(self._period, float):
            return self._period
        if isinstance(self._period, int):
            return self._period

        return self._period()

    def process(self):
        def msg(*args):
            print(f"{self._env.now}:", *args)
        while True:
            with self._from.wait_for_item() as req:
                yield req
            item_inp = self._from.pop()

            p = self._sample_period()
            yield self._env.timeout(p)
            item_out = self._store_builder(item_inp)

            with self._to.wait_for_room() as req:
                yield req
            self._to.add(item_out)
