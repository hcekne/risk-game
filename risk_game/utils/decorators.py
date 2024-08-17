import time
from functools import wraps

# Decorator to measure and accumulate time
def track_turn_time(func):
    @wraps(func)
    def wrapper(self, player, *args, **kwargs):
        start_time = time.time()
        result = func(self, player, *args, **kwargs)
        end_time = time.time()

        turn_duration = end_time - start_time
        player.accumulated_turn_time += turn_duration

        print(f"Time spent this turn: {turn_duration:.2f} seconds")
        print(f"Total accumulated turn time: {player.accumulated_turn_time:.2f} seconds")
        
        return result
    return wrapper