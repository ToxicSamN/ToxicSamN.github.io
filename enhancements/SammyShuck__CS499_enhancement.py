"""
    SammyShuck__CS499_enhancement.py

    Name: Sammy Shuck
    Completion Date: 7/14/2021
    Capstone Class: CS499 Computer Science Capstone

    Original Date: 02/21/2021
    Original Class: CS350 Emerging Systems Architecture and Technology
    Original Assignment: 7-1 Final Project I

    This script will utilize a DHT sensor, light senor and three LEDs (red, green, blue) connected
    to a RaspberryPi.
    The temperature and humidity data will be collected via the DHT sensor but only during the
    daytime. Daytime will be defined by the light sensor and once it is dark data collection
    stops. Additionally, there are three LEDs that will light up to indicate specific situations.

    Green LED lights up when the last conditions are:
      temperature > 60 and < 85, and humidity is < 80%
    Blue LED lights up when the last conditions are:
      temperature > 85 and < 95, and humidity is < 80%
    Red LED lights up when the last conditions are:
      temperature > 95
    Green and Blue LED light up when the last conditions are:
      humidity > 80%

    The JSON structure is specific:
    [
        [ ** temperature and humidity reading 1 **

            [unix timestamp, temperature in F],
            [unix timestamp, humidity in %]
        ],
        [ ** temperature and humidity reading 2 **
            [unix timestamp, temperature in F],
            [unix timestamp, humidity in %]
        ]
    ]
"""

# Import statements
from datetime import datetime
import math
import multiprocessing
import os
import sys
import time
import logging
from influxdb import InfluxDBClient
import grovepi  # pylint: disable=import-error

# Global logger
LOG = logging.getLogger("LOGGER")

# different packages for universal windows platforms than with RPi
if sys.platform == 'uwp':
    import winrt_smbus as smbus  # pylint: disable=import-error

    BUS = smbus.SMBus(1)
else:
    import smbus  # pylint: disable=import-error
    import RPi.GPIO as GPIO  # pylint: disable=import-error

    REV = GPIO.RPI_REVISION
    if REV in (2, 3):
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


class LCD:
    """
    LCD class is an object definition for handling the LCD screen. There are
    many functions and manipulations of the LCD screen. This object will
    handle all of the functionality of the LCD screen.
    """

    # LCD constants
    # this device has two I2C addresses that are constant
    DISPLAY_RGB_ADDR = 0x62
    DISPLAY_TEXT_ADDR = 0x3e

    # class constructor with optional RGB values
    def __init__(self, r=0, g=0, b=0):
        """
        Class constructor for the LCD screen handling with an optional
        RGB background color being passed in. RGB can be changed via
        the public method set_rgb().
        :param r: Red color value, values from 0..255
        :param g: Green color value, values from 0..255
        :param b: Blue color value, values from 0..255
        """
        self.__r = r
        self.__g = g
        self.__b = b
        # text can only be set with prints or prints_no_refresh()
        self.__text = ""

    @staticmethod
    def _delay(t=0.5):
        """
        _delay is a private method for pausing the for `t` seconds
        :param t: float value in seconds to delay. default 0.5s
        """
        time.sleep(t)

    def _return_cursor_home(self):
        """
        _return_cursor_home is a private method that returns the
        cursor to the home position 0x02
        """
        self._send_command(0x02)
        self._delay()

    def _prep_screen(self, no_refresh=False):
        """
        _prep_screen is a private method that prepares the screen for
        content by returning to the home position and clearing the
        screen unless specified by `no_refresh=True`.
        """

        self._return_cursor_home()
        if not no_refresh:
            self.clear_screen()
        self._send_command(0x08 | 0x04)  # display on, no cursor
        self._send_command(0x28)  # two lines
        self._delay()  # delay the default amount of time

    def _send_text(self):
        """
        _send_text is a private method that sends the text to the writer
        checking for new line characters and EOL conditions.
        """

        # LCD screen only has two lines available for content
        #  and a maximum of 16 characters per line. Set the
        #  control variables.
        row = 1  # max 2 rows
        chr_count = 0  # max 16 characters

        # loop through the text content to be written
        #  and prepare each row of text
        for c in self.__text:
            # go to the next row if 16 characters or a new line is found
            if c == '\n' or chr_count == 16:
                # reset chr_count to 0 for the next line
                chr_count = 0
                row += 1
                # if row is greater than 2 stop looping, cannot
                #  add any more text, reached the limit of the
                #  LCD screen
                if row > 2:
                    break

                self._send_command(0xc0)

                if c == '\n':
                    continue

            # keep track of character count
            chr_count += 1

            # write the character to the LCD screen
            self._write(0x40, ord(c))

    def _send_command(self, cmd):
        """
        Public function to send specific SMBus commands to the writer

        :param cmd: byte value
        """
        self._write(0x80, cmd)

    def _write(self, *args):
        """
        _write is a private method that writes the data to the bus

        :param args: array of values for writing. See the SMBus protocol.
        """

        BUS.write_byte_data(self.DISPLAY_TEXT_ADDR, *args)

    def _write_rgb(self):
        """
        _write_rgb is a private method that send the RGB color
        to the LCD background.
        """
        BUS.write_byte_data(self.DISPLAY_RGB_ADDR, 0, 0)
        BUS.write_byte_data(self.DISPLAY_RGB_ADDR, 1, 0)
        BUS.write_byte_data(self.DISPLAY_RGB_ADDR, 0x08, 0xaa)
        BUS.write_byte_data(self.DISPLAY_RGB_ADDR, 4, self.__r)
        BUS.write_byte_data(self.DISPLAY_RGB_ADDR, 3, self.__g)
        BUS.write_byte_data(self.DISPLAY_RGB_ADDR, 2, self.__b)

    def set_rgb(self, r, g, b):
        """
        setter for the R, G, B properties
        :param r: Red color value, values from 0..255
        :param g: Green color value, values from 0..255
        :param b: Blue color value, values from 0..255
        """
        self.__r = r
        self.__g = g
        self.__b = b

        self._write_rgb()

    def clear_screen(self):
        """
        Public function to clears the LCD screen of any contents
        """
        self._send_command(0x01)
        self._delay()  # delay the default amount of time

    def prints(self, text):
        """
        Public method that sets the LCD screen text. Use \n to
        move to the second line, otherwise, the line will auto-wrap.
        This method will clear the screen before writing. If no
        clearing is required see prints_no_refresh.

        :param text: string data to display onto the LCD screen
        """
        self.__text = text
        self._prep_screen()
        self._send_text()

    def prints_no_refresh(self, text):
        """
        Public function that sets the LCD screen text, but updates
        the LCD screen without clearing the display first. Use \n
        to move to the second line, otherwise, the line will auto-wrap

        :param text: string data to display onto the LCD screen
        """
        self.__text = text
        self._prep_screen(no_refresh=True)
        self._send_text()

    def create_custom_char(self, location, pattern):
        """
        Public function that writes a bit pattern to LCD CGRAM.
        Using an array of row patterns, create a custom
        character or image.
        :param location: integer, one of 8 slots (0-7)
        :param pattern: byte array containing the bit pattern, like is found at
               https://omerk.github.io/lcdchargen/
        """
        location &= 0x07  # Make sure the location is 0-7
        self._send_command(0x40 | (location << 3))
        self._write(0x40, pattern)


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
    HIGH = True  # pylint: disable=invalid-name
    LOW = False  # pylint: disable=invalid-name

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
    port configuration. The DHT is the digital humidity and
    temperature sensor.

    :return: DHT Port and DHT Type
    """

    # establish the DHT sensor configuration
    dht_sensor_port = PORT.DIGITAL.D7  # dht sensor location D7
    dht_sensor_type = DHT.BLUE  # sensor type is blue, optionally it could be white

    return [dht_sensor_port, dht_sensor_type]


def collector(out_q, err_q):
    """
    collector is the main program for collecting temperature and humidity data
    :param out_q: multiprocessing queue to send the collected weather data to
    :param err_q: error queue for communicating exceptions to the parent process
    """

    weather_data = []  # list to store the weather data

    # setup necessary ports on the grovePi
    dht_sensor_port, dht_sensor_type = setup_dht()
    led_r, led_g, led_b = setup_leds()

    # setup the LCD handler
    lcd = LCD()
    lcd.set_rgb(0, 128, 64)  # initial LCD background color
    lcd.clear_screen()  # clear the screen of any contents

    light_sensor = PORT.ANALOG.A1  # light sensor to A1
    k_threshold = 10  # Resistance threshold for detecting day vs night

    grovepi.pinMode(light_sensor, "INPUT")  # read sensor input
    grovepi.pinMode(led_r, "OUTPUT")  # red led light output
    grovepi.pinMode(led_g, "OUTPUT")  # green led light output
    grovepi.pinMode(led_b, "OUTPUT")  # blue led light output

    # run realtime collection - no sleep conditions
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

                    # send the updated weather data to be stored to the output
                    #   channel for consumption by writer
                    out_q.put(weather_data)

                    # write to the LCD screen
                    lcd.prints(f"Temp: {celsius_to_fahrenheit(temp)}F\n"
                               f"Humidity: {humidity}%")

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
                    print(datetime.now().strftime("%m/%d/%YT%H:%M:%S") + "\tTemp: " + str(
                        celsius_to_fahrenheit(temp)) + ", Humidity: " + str(humidity))
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

        except IOError as io_err:
            turn_off_leds([led_r, led_g, led_b])
            err_q.put_nowait(io_err)
            LOG.error(io_err)
            break  # break out of the loop
        except KeyboardInterrupt as ki_err:
            turn_off_leds([led_r, led_g, led_b])
            err_q.put_nowait(ki_err)
            LOG.error(ki_err)
            break  # break out of the loop


def writer_to_database(in_q, err_q):
    """
    Writes the temperature and humidity data to a database.
    Expected to be ran as a separate process so the main program is
    not waiting for the file system or network I/O process to complete
    :param in_q: multiprocessing queue containing the weather data to offload
    :param err_q: error queue for communicating exceptions to the parent process
    """
    try:
        # establish influx client connection for writing data to the database
        iclient = InfluxDBClient(host='localhost',
                                 port=8086,
                                 username='influx',
                                 # password stored in os environment variable
                                 password=os.getenv("influx_pwd"),
                                 database='weather',
                                 timeout=5,
                                 retries=1
                                 )
        while True:  # loop to continuously monitor the queue
            # retrieve the data from the queue
            # blocking queue until data is available
            temp_data = in_q.get()

            # write the data to the influxDB
            iclient.write_points(points=temp_data,
                                 time_precision='s',
                                 protocol='json'
                                 )
    # catch all exceptions that may arise and exit
    #  the program
    except BaseException as err:  # pylint: disable=broad-except
        LOG.error(err)
        err_q.put_nowait(err)


if __name__ == "__main__":
    try:
        # Database IO operations are process blocking functions. This
        # has the potential to provide unpredictable behavior. As good
        # practice would have it, blocking operations should be processed
        # concurrently with a data collector.
        # Since dealing with database IO processes it's better to
        # go ahead and have this IO bound process processed concurrently
        # with the temperature readings. These lines defines a multi-
        # processing manager to handle concurrent data operations
        # (collecting vs writing).
        Q_MGR = multiprocessing.Manager()
        DBO_Q = Q_MGR.Queue(maxsize=5)
        ERR_Q = Q_MGR.Queue(maxsize=2)

        # create the database IO operation process
        DBIO_PROCESS = multiprocessing.Process(name="File_IO_Operation",
                                               target=writer_to_database,
                                               kwargs={'in_q': DBO_Q, 'err_q': ERR_Q})
        DBIO_PROCESS.start()
        # create the main process for collecting temp data and manipulating the lcd screen
        COLLECTOR_PROCESS = multiprocessing.Process(name="main",
                                                    target=collector,
                                                    kwargs={'out_q': DBO_Q, 'err_q': ERR_Q})
        COLLECTOR_PROCESS.start()

        # monitor for state changes from the processes
        while True:
            if DBIO_PROCESS.is_alive() and COLLECTOR_PROCESS.is_alive():
                continue  # both processes are still running, continue

            # if only one process is terminated, need to find the one still running.
            # be good and proper and release your resources, terminate the running process
            if not DBIO_PROCESS.is_alive():
                DBIO_PROCESS.terminate()
            if not COLLECTOR_PROCESS.is_alive():
                COLLECTOR_PROCESS.terminate()

            # retrieve the error from the queue
            ERR = ERR_Q.get_nowait()
            raise ERR

    # need capture all exceptions raised and
    # for logging purposes and exit the program
    except BaseException as err:  # pylint: disable=broad-except
        LOG.error(err)
        raise err
