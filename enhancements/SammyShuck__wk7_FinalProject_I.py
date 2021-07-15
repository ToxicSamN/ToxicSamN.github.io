"""
    SammyShuck__wk7_FinalProject_I.py

    Name: Sammy Shuck
    Date: 02/21/2021
    Class: CS350 Emerging Systems Architecture and Technology
    Term: 21EW3
    Assignment: 7-1 Final Project I

    # TODO ENHANCEMENT [CS-499-04] : Best practice add program description at the beginning
"""

# Import statements
from datetime import datetime
# TODO ENHANCEMENT [CS-499-04] : Move import grovepi below builtin imports, design best practice
import grovepi  # pylint: disable=import-error
import json
import math
import os
import sys
import time

# different packages for universal windows platforms than with RPi
if sys.platform == 'uwp':
    import winrt_smbus as smbus  # pylint: disable=import-error

    BUS = smbus.SMBus(1)
else:
    import smbus  # pylint: disable=import-error
    import RPi.GPIO as GPIO  # pylint: disable=import-error

    REV = GPIO.RPI_REVISION
    # TODO ENHANCEMENT [CS-499-03] : merge these comparisons with "in" to if REV in (2, 3):
    if REV == 2 or REV == 3:
        BUS = smbus.SMBus(1)
    else:
        BUS = smbus.SMBus(0)


# Constant declaration
# pylint: disable=too-few-public-methods
class PORT:
    """
    PORT object has constant definitions for the GrovePi riser board
    See https://www.dexterindustries.com/wp-content/uploads/2013/07/grovepi_pinout.png for more
    details.
    """

    # pylint: disable=too-few-public-methods
    class ANALOG:
        """
        ANALOG ports are defined as
        A0 = 0,
        A1 = 2,
        A2 = 3,
        GrovePi sockets A0,A1,A2 use the AD converter and support analogRead() values 0-1023
        Can only use analogRead() with A0, A1, A2 (aka D14, D15, D16)
        """

        A0 = 0
        A1 = 1
        A2 = 2

    # pylint: disable=too-few-public-methods
    class DIGITAL:
        """
        DIGITAL ports are defined as
        D2 = 2,
        D3 = 3,
        D4 = 4,
        D5 = 5,
        D6 = 6,
        D7 = 7,
        D8 = 8
        GrovePi sockets D2-D8 are digital and support 1-bit input/output, values 0-1,
        using digitalRead() and digitalWrite().

        GrovePi sockets D3,D5,D6 also support Pulse Width Modulation (PWM) which means you can
        write 8-bit values 0-255 with analogWrite().
        """

        D2 = 2
        D3 = 3
        D4 = 4
        D5 = 5
        D6 = 6
        D7 = 7
        D8 = 8

    # pylint: disable=too-few-public-methods
    class PWM:
        """
        Pulse Width Modulation (PWM) ports are defined as
        PWM1 = D3 = 3,
        PWM2 = D5 = 5,
        PWM3 = D6 = 6,

        GrovePi sockets D3,D5,D6 also support Pulse Width Modulation (PWM) which means you can
        write 8-bit values 0-255 with analogWrite()
        """

        PWM1 = 3
        PWM2 = 5
        PWM3 = 6


# pylint: disable=too-few-public-methods
class LED:
    """
    LED Object constants for ON and OFF for better readability
    """
    ON = 1
    OFF = 0


# pylint: disable=too-few-public-methods
class DHT:
    """
    LCD Type definition constants for better readability
    """
    BLUE = 0
    WHITE = 1

# TODO ENHANCEMENT [CS-499-03] : Create an LCD Object handler to control LCD functionality

def celsius_to_fahrenheit(degree):
    """
    Converts Celsius to Fahrenheit
    :param degree: float value in degrees Celsius
    :return: float value in degrees Fahrenheit
    """
    return float(float(degree) * (9.0/5.0) + 32)


def safe_divsion(num, den):
    """
    Simple division function to check for a ZeroDivisionError and to return
    0 in this case.
    :param num: numerator
    :param den: denominator
    :return:
    """
    try:
        div = num/den
        return div
    except ZeroDivisionError:
        return 0


def is_daylight(light_sensor, k_threshold):
    """
    isDaylight is a function for reading the light sensor and evaluating
    the sensor based upon an input threshold defining daylight.
    If the threshold is met or below the threshold then this indicates
    daylight. Since daylight is defined differently around the world
    this function avoids hard-coded daylight threshold. However,, this
    typically is around 10K resistance.

    Typically, the resistance of the LDR or Photoresistor will decrease when the ambient light
    intensity increases.
    This means that the output signal from this module will be HIGH in bright light, and LOW in
    the dark.
    :param light_sensor: Light sensor port of the GrovePi
    :param k_threshold: Daylight definition in K resistance
    :return: HIGH or LOW (boolean)
    """

    # constants
    HIGH = True
    LOW = False

    # read analog reading from sensor
    sensor_value = grovepi.analogRead(light_sensor)
    # if sensor value is 0 then there was likely an issue reading the sensor, so try again
    if sensor_value == 0:
        sensor_value = grovepi.analogRead(light_sensor)

    # Calculate specific resistance (K)
    # using a safe division helper function here to prevent any ZeroDivisionError exceptions
    resistance = safe_divsion(float(1023 - sensor_value) * 10, sensor_value)

    # Typically, the resistance of the LDR or Photoresistor will decrease when the ambient light
    # intensity increases.
    # This means that the output signal from this module will be HIGH in bright light, and LOW in
    # the dark.
    if resistance <= k_threshold and not sensor_value == 0:
        print("It is Daylight: sensor value: " + str(sensor_value) + ", resistance: " + str(
            resistance) + ", resistance threshold: " + str(k_threshold))
        return HIGH

    return LOW


def turn_on_leds(leds):
    """
    turn_on_leds is a helper function for processing the turning on the LED lights.
    :param leds: array of led sensor locations
    :return: None
    """

    try:
        for led in leds:
            grovepi.digitalWrite(led, LED.ON)
    except BaseException as err:
        raise err


def setup_leds():
    """
    setup_leds is a helper function for setting the LED port connections.
    :return: LED red, green, and blue connections
    """
    # LED port definitions for red, green, blue LEDs
    led_r = PORT.DIGITAL.D2  # red LED to D2
    led_g = PORT.DIGITAL.D4  # green LED to D4
    led_b = PORT.DIGITAL.D3  # blue LED to D3

    return [led_r, led_g, led_b]


def turn_off_leds(leds):
    """
        turn_off_leds is a helper function for processing the turning off the LED lights.
        :param leds: array of led sensor locations
        :return: None
    """
    try:
        for led in leds:
            grovepi.digitalWrite(led, LED.OFF)
    except BaseException as err:
        raise err


def setup_dht():
    """
    setup_lcd is a helper function for setting the DHT sensor
    port configuration.
    :return: DHT Port and DHT Type
    """
    # establish a new LCD object
    dht_sensor_port = PORT.DIGITAL.D7  # dht sensor location D7
    dht_sensor_type = DHT.BLUE  # sensor type is blue, optionally it could be white

    return [dht_sensor_port, dht_sensor_type]

# TODO ENHANCEMENT [CS-499-04] : Implement a new function for handling the database writing
# TODO ENHANCEMENT [CS-499-05] : Security Best Practices requires a log of all errors.

def main():
    """
    Main program for collecting temperature and humidity data
    """

    weather_data = []  # list to store the weather data

    # setup necessary ports on the grovePi
    dht_sensor_port, dht_sensor_type = setup_dht()
    led_r, led_g, led_b = setup_leds()
    light_sensor = PORT.ANALOG.A1  # light sensor to A1

    k_threshold = 10  # Resistance threshold for detecting day vs night

    grovepi.pinMode(light_sensor, "INPUT")  # read sensor input
    grovepi.pinMode(led_r, "OUTPUT")  # red led light output
    grovepi.pinMode(led_g, "OUTPUT")  # green led light output
    grovepi.pinMode(led_b, "OUTPUT")  # blue led light output

    while True:
        try:
            # Turn off LEDs to reset LED status prior to sensor readings
            # since only the LED status should exist if it is daylight
            turn_off_leds([led_r, led_g, led_b])

            if is_daylight(light_sensor, k_threshold):
                # collect the data from the sensor
                [temp, humidity] = grovepi.dht(dht_sensor_port, dht_sensor_type)
                if math.isnan(temp) is False and math.isnan(humidity) is False:

                    # for some strange reason canvasJS needs the extra 0's for unixtime to work
                    unixtime = int(time.time()) * 1000

                    # dict for preparation to send JSON to database

                    # configure the canvasJS JSON structure
                    # [
                    # 	[ ** temperature and humidity reading 1 **

                    # 		[unix timestamp, temperature in F],
                    # 		[unix timestamp, humidity in %]
                    # 	],
                    # 	[ ** temperature and humidity reading 2 **
                    # 		[unix timestamp, temperature in F],
                    # 		[unix timestamp, humidity in %]
                    # 	]
                    # ]
                    weather_data.append([[unixtime, celsius_to_fahrenheit(temp)],
                                         [unixtime, humidity]])

                    # TODO ENHANCEMENT [CS-499-03] : Add LCD writing of temperature and humidity data
                    # TODO ENHANCEMENT [CS-499-04] : Send the data to the writer channel instead of the writer function

                    # send the updated weather data to the JSON file
                    # obtain output file
                    outfile = os.getenv("CS350_OUTPUT", "data.json")
                    # clear the contents of the data.json file initially
                    with open(outfile, 'w+') as f_out:
                        # this truncates the file and will replace any existing data in the file
                        json.dump("", f_out)
                        f_out.close()  # be good and proper
                    print("Writing Weather Data to File " + outfile)
                    try:
                        # write the data to a file
                        # using /tmp/ as every *nix system has this dir available as
                        #  R/W for everyone
                        with open(outfile, 'w+') as f_out:
                            # this truncates the file and will replace any existing data in the file
                            json.dump(weather_data, f_out)
                            f_out.close()  # be good and proper
                    except IOError as io_err:
                        turn_off_leds([led_r, led_g, led_b])
                        raise io_err

                    # Program Specifications
                    # Green LED lights up when the last conditions are:
                    #   temperature > 60 and < 85, and humidity is < 80%
                    # Blue LED lights up when the last conditions are:
                    #   temperature > 85 and < 95, and humidity is < 80%
                    # Red LED lights up when the last conditions are:
                    #   temperature >= 95
                    # Green and Blue LED light up when the last conditions are:
                    #   humidity >= 80%

                    # start by turning off the LEDs
                    print(datetime.now().strftime("%m/%d/%YT%H:%M:%S") + "\tTemp: " +
                          str(celsius_to_fahrenheit(temp)) + ", Humidity: " + str(humidity))
                    if humidity >= 80:
                        print("LED ON: GREEN and BLUE")
                        turn_on_leds([led_g, led_b])
                    elif celsius_to_fahrenheit(temp) >= 95:
                        print("LED ON: RED")
                        turn_on_leds([led_r])
                    elif 60 < celsius_to_fahrenheit(temp) < 85 and humidity < 80:
                        print("LED ON: GREEN")
                        turn_on_leds([led_g])
                    elif 85 < celsius_to_fahrenheit(temp) < 95 and humidity < 80:
                        print("LED ON: BLUE")
                        turn_on_leds([led_b])

            # TODO ENHANCEMENT [CS-499-03] : Remove the delay and collect real-time
            # Program specification states to only collect data every 30 minutes
            time.sleep(1800)  # run every 30 minutes

        except IOError as io_err:
            turn_off_leds([led_r, led_g, led_b])
            # TODO ENHANCEMENT [CS-499-05] : Security Best Practices requires a log of all errors.
            raise io_err
        except KeyboardInterrupt as ki_err:
            turn_off_leds([led_r, led_g, led_b])
            # TODO ENHANCEMENT [CS-499-05] : Security Best Practices requires a log of all errors.
            raise ki_err


if __name__ == "__main__":
    try:
        # TODO ENHANCEMENT [CS-499-04] : Add a Multi-Processor handler that will run two processes { collector | database }
        main()
    except BaseException as err:
        # TODO ENHANCEMENT [CS-499-05] : Security Best Practices requires a log of all errors.
        raise err
