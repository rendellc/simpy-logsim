from typing import Callable, Any

from . import Env

from . import Store

GenFactory = Callable[[], Any]


def gen(env: Env, store: Store, factory: GenFactory, period: float):
    while True:
        # print(f"{env.now}: making assembly")
        item = factory()
        yield from store.add(item)
        yield env.timeout(period)
