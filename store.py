import simpy
from collections import deque

from typing import TypeVar, Generic, Callable
T = TypeVar("T")
U = TypeVar("U")


class Store(Generic[T]):
    def __init__(self, env, max_capacity):
        self._xs: list[T] = []
        self._container = simpy.Container(env, max_capacity, init=0)

    def add(self, x: T):
        with self._container.put(1) as req:
            yield req

        self._xs.append(x)

    def len(self) -> int:
        return len(self._xs)

    def pop(self) -> T:
        with self._container.get(1) as req:
            yield req
        return self._xs.pop(-1)

    def get(self) -> T:
        with self._container.get(1) as req:
            yield req
        with self._container.put(1) as req:
            yield req
        return self._xs[-1]


def move(_from: Store[T], _to: Store[U], tf: Callable[T, U]):
    x = yield from _from.pop()
    yield from _to.add(tf(x))
