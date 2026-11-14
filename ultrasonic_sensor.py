import math
import utime
from hcsr04 import HCSR04
import log


class UltrasonicSensor:
    """Measures the distance to the water surface and converts it to a fill level."""

    # The HC-SR04 cannot reliably measure distances below this value.
    MIN_SENSOR_DISTANCE_CM = 2

    def __init__(self, trigger_pin, echo_pin, distance_full_cm, distance_empty_cm,
                 measurements_per_reading=10, max_plausible_distance_cm=100):
        if distance_full_cm >= distance_empty_cm:
            raise ValueError(
                "DISTANCE_FULL_CM ({}) must be smaller than DISTANCE_EMPTY_CM ({}): "
                "the sensor is closer to the water when the tank is full.".format(
                    distance_full_cm, distance_empty_cm))
        if distance_full_cm < self.MIN_SENSOR_DISTANCE_CM:
            log.warn("DISTANCE_FULL_CM is below the HC-SR04 minimum range of ~{} cm".format(
                self.MIN_SENSOR_DISTANCE_CM))

        self.distance_full_cm = distance_full_cm
        self.distance_empty_cm = distance_empty_cm
        self.measurement_range_cm = distance_empty_cm - distance_full_cm
        self.measurements_per_reading = measurements_per_reading
        self.max_plausible_distance_cm = max_plausible_distance_cm
        self.sensor = HCSR04(trigger_pin=trigger_pin, echo_pin=echo_pin)

    def read_distance(self, clamp=True):
        """Return the filtered distance in cm, or None if no valid measurement was taken.

        With clamp=True, distances beyond the "empty" distance are clamped to it.
        """
        log.debug("---Read Distance---")
        measurements = []

        for _ in range(self.measurements_per_reading):
            try:
                distance = self.sensor.distance_cm()
            except OSError as ex:
                log.debug("Sensor error: ", ex)
                distance = -1

            if distance <= 0 or distance > self.max_plausible_distance_cm:
                log.debug("Out of range: ", distance)
            else:
                if clamp and distance > self.distance_empty_cm:
                    distance = self.distance_empty_cm
                measurements.append(distance)
                log.debug("Distance: ", distance, " cm")
            utime.sleep_ms(100)

        count = len(measurements)
        if count == 0:
            log.warn("No valid ultrasonic measurements -- check wiring and sensor position")
            return None

        # Remove outliers: keep only values within one standard deviation of the mean
        mean = sum(measurements) / count
        std_dev = (sum([(m - mean) ** 2 for m in measurements]) / count) ** 0.5
        # Small epsilon so identical readings are not rejected due to float rounding of the mean
        tolerance = std_dev + 0.01
        valid = [m for m in measurements if mean - tolerance <= m <= mean + tolerance]
        if not valid:
            valid = measurements
        distance = sum(valid) / len(valid)

        log.debug("Measurements: ", measurements)
        log.debug("Mean: ", mean, " std dev: ", std_dev)
        log.debug("Valid measurements: ", valid)
        log.debug("Calculated distance: ", distance)
        return distance

    def distance_to_level(self, distance_cm):
        """Convert a distance in cm to a fill level in percent (0-100)."""
        offset = max(0, distance_cm - self.distance_full_cm)
        empty_percent = math.ceil(offset / self.measurement_range_cm * 100)
        return max(0, min(100, 100 - empty_percent))

    def read_waterlevel(self):
        """Return the water level in percent (0-100), or None if the sensor gave no valid reading."""
        distance = self.read_distance()
        if distance is None:
            return None
        level = self.distance_to_level(distance)
        log.debug("Water level: ", level, " %")
        return level
