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


    # HC-SR04 returns ~500 cm on echo timeout; anything this far is not a real tank reading
    MAX_PLAUSIBLE_DISTANCE_CM = 100

    def read_distance(self, measurements_per_round=10):
        """Return the filtered distance in cm, or None if no valid measurement was taken."""
        print("---Read Distance---")
        measurements = []

        for i in range(0, measurements_per_round):
            try:
                distance = self.sensor.distance_cm()
            except OSError as ex:
                print("Sensor error: ", ex)
                distance = -1

            if distance <= 0 or distance > self.MAX_PLAUSIBLE_DISTANCE_CM:
                print("Out of range: ", distance)
            elif distance > self.max_distance_cm:
                measurements.append(self.max_distance_cm)
                print("Distance: ", distance, " cm")
            else:
                measurements.append(distance)
                print("Distance: ", distance, " cm")
            utime.sleep_ms(100)

        print("Measurements: ", measurements)
        measurementsCount = len(measurements)
        if measurementsCount == 0:
            print("No valid measurements")
            return None

        sample_mean = sum(measurements) / measurementsCount
        print("Sample mean: ", sample_mean)
        sample_std_dev = (sum([(m - sample_mean) ** 2 for m in measurements]) / measurementsCount) ** 0.5
        print("Sample standard deviation: ", sample_std_dev)
        # Small epsilon so identical readings are not rejected due to float rounding of the mean
        tolerance = sample_std_dev + 0.01
        lowestAllowedValue = sample_mean - tolerance
        highestAllowedValue = sample_mean + tolerance
        print("Lowest allowed value: ", lowestAllowedValue)
        print("Highest allowed value: ", highestAllowedValue)

        valid_measurements = [m for m in measurements if lowestAllowedValue <= m <= highestAllowedValue]
        print("Valid measurements: ", valid_measurements)
        if not valid_measurements:
            valid_measurements = measurements
        calculated_distance = sum(valid_measurements) / len(valid_measurements)
        print("Calculated distance: ", calculated_distance)

        return calculated_distance

    def read_waterlevel(self):
        """Return the water level in percent (0-100), or None if the sensor gave no valid reading."""
        distance = self.read_distance()
        if distance is None:
            return None
        abs_distance = distance - self.min_distance_cm
        if abs_distance < 0:
            abs_distance = 0
        distance_percent = math.ceil(abs_distance / self.measurement_range * 100)
        print("Abs distance: ", abs_distance)
        print("Distance %: ", distance_percent)
        waterlevel = 100 - distance_percent
        waterlevel = max(0, min(100, waterlevel))
        print("Fuellstand: ", waterlevel)
        return waterlevel
