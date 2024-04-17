import simpy as s


def clock(env, name, tick):
    while True:
        print(name, env.now)
        yield env.timeout(tick)


env = s.Environment()
env.process(clock(env, "fast", 1))
env.process(clock(env, "slow", 4))

env.run(until=10)
