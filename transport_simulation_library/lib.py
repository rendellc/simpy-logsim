from __future__ import annotations

from typing import Any
import simpy

from typing import Union, Generic, Callable, Protocol, Iterator
from typing import Protocol


class Env:
    def __init__(self, realtime: Union[None, float] = None):
        if realtime:
            self._env = simpy.RealtimeEnvironment(
                factor=1 / realtime, strict=False)
        else:
            self._env = simpy.Environment()

    def log(self, *args):
        print("Time", self._env.now, ":", *args)

    def timeout(self, duration: float):
        return self._env.timeout(duration)

    def process(self, event):
        self._env.process(event)

    def run(self, until: float):
        self._env.run(until)

    def now(self) -> float:
        return self._env.now

    def add_agent(self, name: str) -> Workforce:
        return Agent(self, name)

    def add_workforce(self, number: int) -> Workforce:
        return Workforce(self, number)

    def add_store[T](self, capacity: int) -> Store[T]:
        return Store[T](self, capacity)


class Store[T]:
    def __init__(self, env: Env, max_capacity: int):
        self._env: Env = env
        self._xs: list[T] = []
        self._container = simpy.Container(env._env, max_capacity, init=0)

    def env(self) -> Env:
        return self._env

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


class Agent:
    def __init__(self, env: Env, name: str):
        self._name: str = name
        self._env: Env = env
        self._res: simpy.Resource = simpy.Resource(env._env, capacity=1)
        self._tasks: list[Task] = []

    def log(self, *args):
        self._env.log(*args)

    def add_task(self, task: Task):
        self._tasks.append(task)

    def __enter__(self):
        return self._res.request().__enter__()

    def __exit__(self, exc_type, exc_value, exc_tb):
        return self._res.request().__exit__(exc_type, exc_value, exc_tb)

    def _select_task(self) -> Union[Task, None]:
        task_best = None
        priority_best = -float('inf')
        for task in self._tasks:
            p = task.priority()
            if p > 0 and p > priority_best:
                task_best = task
                priority_best = p

        return task_best

    def process(self) -> Iterator[None]:
        while True:
            task = self._select_task()
            if task is None:
                self.log("nothing to do")
                yield self._env.timeout(60)
                continue

            self.log("starting task:", task.name())
            yield from task.perform()


class Workforce:
    def __init__(self, env: Env, size: int):
        self._res = simpy.Resource(env._env, capacity=size)

    def request(self):
        return self._res.request()

    def count(self):
        return self._res.count

    def capacity(self):
        return self._res.capacity


class Task(Protocol):
    def name(self) -> str: ...

    def priority(self) -> float: ...

    def perform(self) -> Iterator[None]: ...
