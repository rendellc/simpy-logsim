import simpy as s
from dataclasses import dataclass
from typing import NewType, Union

import store
from store import Store
from process import GenericProcess
from random import randint

from collections import namedtuple

Screw = namedtuple("Screws", "")
Frame = namedtuple("Frame", "")
Motor = namedtuple("Motor", "")


@dataclass
class Assy:
    screws: list[Screw]
    frame: Frame
    motor: Motor


def assembly_generator(env, store, period):
    while True:
        yield env.timeout(period)
        # print(f"{env.now}: making assembly")
        yield from store.add(
            Assy(
                screws=[Screw() for _ in range(randint(90, 110))],
                frame=Frame(),
                motor=Motor(),
            )
        )


def assembly_dissassemble(
    env: s.Environment,
    store_assy: Store,
    store_screws: Store,
    store_motor: Store,
    store_frame: Store,
    screw_period: float,
    motor_period: float,
    frame_move_period: float,
):
    while True:
        assy = yield from store_assy.get()
        # print("got", assy)

        while len(assy.screws) > 0:
            screw = yield from assy.screws.pop(-1)
            yield env.timeout(screw_period)
            yield from store_screws.add(screw)

        motor = assy.motor
        assy.motor = None
        yield env.timeout(motor_period)
        yield from store_motor.add(motor)

        yield env.timeout(frame_move_period)
        yield from store.move(store_assy, store_frame, lambda a: a.frame)


realtimefactor = None
if realtimefactor:
    env = s.RealtimeEnvironment(factor=1 / realtimefactor, strict=False)
else:
    env = s.Environment()

store_assy = Store[Assy](env, 1)
store_screws = Store[Screw](env, 1000)
store_motor = Store[Motor](env, 2)
store_frame = Store[Frame](env, 1000)

env.process(
    assembly_dissassemble(
        env,
        store_assy,
        store_screws,
        store_motor,
        store_frame,
        screw_period=15,
        motor_period=1200,
        frame_move_period=800,
    )
)

# num_inp_to_mids = 5
# inp_to_mids = [
#     GenericProcess(env, store_frame, store_screws, lambda x: x, 120)
#     for _ in range(num_inp_to_mids)
# ]
# num_mid_to_outs = 5
# mid_to_outs = [
#     GenericProcess(env, store_screws, store_output, lambda x: x, 60)
#     for _ in range(num_mid_to_outs)
# ]
env.process(assembly_generator(env, store_assy, 24*3600))
# for p in inp_to_mids:
#     env.process(p.process())
# for p in mid_to_outs:
#     env.process(p.process())


# def monitoring(env, period):
#     while True:
#         print(
#             {
#                 "time": env.now,
#                 "input": store_inp.len(),
#                 "middle": store_mid.len(),
#                 "output": store_out.len(),
#             },
#         )
#         yield env.timeout(period)
# env.process(monitoring(env, 300))

# env.run(until=12*24 * 3600)
env.run(until=7*24 * 3600)
print("Time:", env.now)
print("Assy:", store_assy.len())
print("Screws:", store_screws.len())
print("Motors:", store_motor.len())
print("Frames:", store_frame.len())
