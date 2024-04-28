from functools import partial, wraps
import simpy


def trace(env, callback):
    def get_wrapper(env_step, callback):
        @wraps(env_step)
        def tracing_step():
            if len(env._queue) > 0:
                callback(env._queue[0])

            return env_step()
        return tracing_step

    return get_wrapper(env.step, callback)
