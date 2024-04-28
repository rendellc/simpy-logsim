from random import randint
from collections import namedtuple
from dataclasses import dataclass

import transport_simulation_library as tsl

Screw = namedtuple("Screws", "")
Frame = namedtuple("Frame", "")
Motor = namedtuple("Motor", "")


@dataclass
class Assy:
    screws: list[Screw]
    frame: Frame
    motor: Motor


def create_assy():
    return Assy(
        screws=[Screw() for _ in range(randint(90, 110))],
        frame=Frame(),
        motor=Motor(),
    )


def remove_screw(
    env, workforce: tsl.Workforce, assy: Assy, store_screws: tsl.Store, screw_period: float
):
    with workforce.request() as req:
        yield req
        if len(assy.screws) == 0:
            return

        screw = yield from assy.screws.pop(-1)
        yield env.timeout(screw_period)
        yield from store_screws.add(screw)


def remove_screws(
    env: tsl.Env,
    people: tsl.Workforce,
    assy: Assy,
    store_screws: tsl.Store,
    screw_period: float,
):
    for _ in range(len(assy.screws)):
        env.process(remove_screw(env, people, assy,
                                 store_screws, screw_period))

    yield from tsl.utils.wait_until(env, lambda: len(assy.screws) == 0)


def assy_dissassemble(
    env: tsl.Env,
    people: tsl.Workforce,
    store_assy: tsl.Store,
    store_screws: tsl.Store,
    store_motor: tsl.Store,
    store_frame: tsl.Store,
    screw_period: float,
    motor_period: float,
    frame_move_period: float,
):
    while True:
        with people.request() as req:
            yield req
            assy = yield from store_assy.get()
        print("Starting dissassembly")

        yield from remove_screws(env, people, assy, store_screws, screw_period)
        print("All screws removed")

        with people.request() as req:
            yield req
            motor = assy.motor
            assy.motor = None
            yield env.timeout(motor_period)
            yield from store_motor.add(motor)
        print("Motor removed")

        with people.request() as req:
            yield req
            yield env.timeout(frame_move_period)
            yield from tsl.utils.move(store_assy, store_frame, lambda a: a.frame)
        print("Frame moved to storage")


data = []


def monitor_env(env):
    global data
    d = {
        "time": env.now(),
        "people": f"{people.count()}/{people.capacity()}",
        "assy": store_assy.len(),
        "screws": store_screws.len(),
        "motor": store_motor.len(),
        "frame": store_frame.len(),
    }
    data.append(d)
    print(d)


def monitor_event(event):
    monitor_env(event.env)


def monitoring(env, period):
    while True:
        monitor_env(env)
        yield env.timeout(period)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-p", "--people", type=int,
                        help="number of people to make available",
                        required=True
                        )
    parser.add_argument("--realtimefactor", type=float,
                        help="realtime factor")
    parser.add_argument("--monitor", action="store_true",
                        help="enable monitoring")
    args = parser.parse_args()

    realtimefactor = args.realtimefactor
    env = tsl.Env(realtimefactor)

    people = env.add_workforce(args.people)
    store_assy = env.add_store(1)
    store_screws = env.add_store(100000)
    store_motor = env.add_store(1000)
    store_frame = env.add_store(1000)

    env.process(
        assy_dissassemble(
            env,
            people,
            store_assy,
            store_screws,
            store_motor,
            store_frame,
            screw_period=15,
            motor_period=1200,
            frame_move_period=800,
        )
    )

    env.process(tsl.gen(env, store_assy, create_assy, 1200))
    if args.monitor:
        mon_period = args.realtimefactor if args.realtimefactor else 300
        env.process(monitoring(env, mon_period))
        # monitor.trace(env, monitor_event)

    # env.run(until=12*24 * 3600)
    env.run(until=7*7.5 * 3600)
    print("Time:", env.now())
    print("Assy:", store_assy.len())
    print("Screws:", store_screws.len())
    print("Motors:", store_motor.len())
    print("Frames:", store_frame.len())

    print(data)
