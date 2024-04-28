import transport_simulation_library as tsl
from dataclasses import dataclass

from typing import Iterator


@dataclass
class FiberRoll:
    decitex: float
    meters: float

    def density(self) -> float:
        """Return density in gram per meter"""
        return self.decitex / 10000


class TaskLoadTwisterRack(tsl.Task):
    def __init__(
        self,
        agent: tsl.Agent,
        fiber_store: tsl.Store[FiberRoll],
        twister_rack: tsl.Store[FiberRoll],
    ):
        self._agent = agent
        self._store_fiber = fiber_store
        self._store_twister = twister_rack

    def name(self):
        return "Load Twister Rack"

    def priority(self):
        if self._store_twister.len() >= 16:
            return -1

        return 1

    def perform(self) -> Iterator[None]:
        if self._store_twister.len() >= 16:
            return None

        self._agent.log("Moving from fiber store")
        yield from tsl.utils.move(self._store_fiber, self._store_twister, 120)
        self._agent.log("Rolls now in fiber store:", self._store_twister.len())


def run():
    print("Starting otsas simulation")

    env = tsl.Env(60)
    fiber_store: tsl.Store[FiberRoll] = env.add_store(500)
    for _ in range(100):
        yield from fiber_store.add(FiberRoll(1234.5, 10000))

    print("Fiber store initialized with", fiber_store.len(), "rolls")
    twister_rack: tsl.Store[FiberRoll] = env.add_store(16)

    agent = env.add_agent("Person A")
    agent.add_task(
        TaskLoadTwisterRack(agent, fiber_store, twister_rack)
    )

    env.process(agent.process())

    # # twist 16 at a time to a single roll
    # # a. if an input roll empties, then a person may stop the
    # #    machine, refill the emptied roll, and tie it togheter
    # #    with the prior roll
    # # load twisted rolls onto bobin twister
    # # twist 20 twisted rolls into a single bobin
    # # load bobins onto core rope maker
    # # twist 12 bobins to core rope
    # # a. all bobins must be loaded before this can start.
    # # b. once running, no more bobins may be loaded

    env.run(3600)


def main():
    r = run()
    try:
        while True:
            next(r)
    except StopIteration:
        pass


if __name__ == "__main__":
    main()
