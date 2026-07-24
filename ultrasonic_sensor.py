# from machine import Pin
import utime
import math
from hcsr04 import HCSR04

class UltrasonicSensor:

    trigPin = 16 # HC-SR04 trigger pin 
    echoPin = 17 # HC-SR04 echo pin 
    LOW = 0
    HIGH = 1

    def __init__(self, min_distance_cm, max_distance_cm):
        self.min_distance_cm = min_distance_cm
        self.max_distance_cm = max_distance_cm
        self.measurement_range = (max_distance_cm - min_distance_cm)
        self.sensor = HCSR04(trigger_pin=16, echo_pin=17)


    def read_distance(self, measurements_per_round=10):
        # trigger_pin = Pin(trigPin, mode=Pin.IN)
        # echo_pin = Pin(echoPin, mode=Pin.IN)
        # sensor = HCSR04(trigger_pin=16, echo_pin=17)

        print("---Read Distance---");  
        measurements = []

        for i in range(0, measurements_per_round):
            distance = self.sensor.distance_cm()
            if distance <= 0:
                print("Out of range")
                # measurements.append(0)
            elif distance > self.max_distance_cm:
                measurements.append(self.max_distance_cm)
                print("Distance: ", distance, " cm")
            else:
                measurements.append(distance)
                print("Distance: ", distance, " cm")
            utime.sleep_ms(100)

        print("Measurements: ", measurements)
        non_null_measurements = [m for m in measurements if m > 0]
        print("Non-null measurements: ", non_null_measurements)
        measurementsCount = len(non_null_measurements)
        print("Measurements count: ", measurementsCount)

        sample_mean = sum(non_null_measurements) / measurementsCount
        print("Sample mean: ", sample_mean)
        sample_std_dev = (sum([(m - sample_mean) ** 2 for m in non_null_measurements]) / measurementsCount) ** 0.5
        print("Sample standard deviation: ", sample_std_dev)
        lowestAllowedValue = sample_mean - sample_std_dev
        highestAllowedValue = sample_mean + sample_std_dev
        print("Lowest allowed value: ", lowestAllowedValue)
        print("Highest allowed value: ", highestAllowedValue)

        valid_measurements = [m for m in non_null_measurements if lowestAllowedValue <= m <= highestAllowedValue]
        print("Valid measurements: ", valid_measurements)
        calculated_distance = sum(valid_measurements) / len(valid_measurements)
        print("Calculated distance: ", calculated_distance)

        return calculated_distance

    def read_waterlevel(self):
        distance = self.read_distance()
        abs_distance = distance - self.min_distance_cm
        if abs_distance < 0:
            abs_distance = 0
        print("Abs distance: ", abs_distance)
        print("Distance %: ",  math.ceil(abs_distance / self.measurement_range * 100))
        print("Fuellstand: ", 100 - math.ceil(abs_distance / self.measurement_range * 100))
        waterlevel = 100 - math.ceil(abs_distance / self.measurement_range * 100)
        result = waterlevel if waterlevel <= 100 else 100
        return result