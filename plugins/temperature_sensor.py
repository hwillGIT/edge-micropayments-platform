import random

class TemperatureSensor:
    @staticmethod
    def read_temperature():
        # 10% chance of error
        if random.random() < 0.10:
            # randomly choose between -1 or None
            return random.choice([-1, None])
        # otherwise return a normal simulated human body temperature in celsius
        return round(random.uniform(37.0, 40.55), 1)
