from typing import Callable
from typing import TypeVar

from . import Env
from . import Store


U = TypeVar("U")
V = TypeVar("V")


def move(_from: Store[U], _to: Store[V], duration: float, tf: Callable[U, V] = None):
    assert _from.env() is _to.env()
    if tf is None:
        def tf(x): return x

    x = yield from _from.pop()
    yield _from.env().timeout(duration)
    yield from _to.add(tf(x))


def wait_until(env: Env, predicate: Callable[[], bool]):
    while not predicate():
        yield env.timeout(1)
