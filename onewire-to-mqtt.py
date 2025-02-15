#!/usr/bin/env python
import time
import sys
import configparser
import paho.mqtt.client as mqtt
from w1thermsensor import W1ThermSensor
from loguru import logger as log
import signal

config_FILE = "config.ini"

class OneWireToMQTT():

    def __init__(self):
        signal.signal(signal.SIGINT, self.do_exit)
        signal.signal(signal.SIGTERM, self.do_exit)

        self.config = self.load_config()

        self.pollInterval = self.config.getint("general", "pollinterval", fallback=30)
        self.statusTopic = self.config.get("general", "statustopic", fallback="onewire-to-mqtt/status")

        self.setup_logging()
        self.setup_mqtt()


    def do_exit(self, signum, frame):
        log.warning('exiting')
        exit()

    # Load self.configuration
    def load_config(self):
        config = configparser.ConfigParser()
        config.read(config_FILE)
        return config

    # MQTT on_connect callback
    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            log.debug("Connected to MQTT Broker successfully")
        else:
            log.error(f"Failed to connect, return code {reason_code}")

    # Setup MQTT connection
    def setup_mqtt(self):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
        client.on_connect = self.on_connect

        # Set MQTT credentials if provided
        if self.config.has_option("mqtt", "username") and self.config.has_option("mqtt", "password"):
            username = self.config.get("mqtt", "username")
            password = self.config.get("mqtt", "password")
            if username and password:
                client.username_pw_set(username, password)
            else:
                log.error("MQTT username or password is missing in the configuration.")

        # Enable TLS if self.configured
        if self.config.getboolean("mqtt", "tls", fallback=False):
            try:
                client.tls_set()  # You may need to provide CA certificates if required
                log.info("TLS enabled for MQTT connection.")
            except Exception as e:
                log.error(f"Failed to set TLS: {e}")
                sys.exit(1)

        try:
            log.info("Connecting to MQTT broker...")
            client.connect(
                self.config.get("mqtt", "host"),
                self.config.getint("mqtt", "port", fallback=1883),
                60,
            )
        except Exception as e:
            log.error(f"MQTT connection failed: {e}")
            raise e

        client.loop_start()
        self.mqttClient = client


    def setup_logging(self):
        logLevel = self.config.get("log", "level", fallback="INFO").upper()
        if logLevel not in {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}:
            log.error("""[log] level must be one of "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR" or "CRITICAL" """)
            exit(1)

        log.remove()
        log.add(
            self.config.get("log", "file", fallback="onewire-to-mqtt.log"),
            rotation="1 GB",
            retention=2,
            level=logLevel,
            colorize=True,
            format="{time:YYYY-MMM-DD HH:mm:ss} | <level>{level}</level> | <level>{message}</level>",
            backtrace=True,
            diagnose=True,
            watch=True,
        )

        # log to stdout if specified
        if self.config.getboolean("log", "stdout", fallback=False):
            log.add(print, colorize=True, format="<level>{message}</level>", level=logLevel)


    def get_sensors(self):
        sensorsCfg = dict(self.config.items("sensors"))

        sensors = W1ThermSensor.get_available_sensors()
        while not sensors:
            log.error("No sensors found!")
            log.info("trying again in 3 seconds...")
            time.sleep(3)

        log.info(f"Sensors found:")

        for sensor in sensors:
            log.info(f"Type: {sensor.type}, ID: {sensor.id}")

            sensorAltID = f"28-{sensor.id}"
            sensor.topic = sensorsCfg.get(sensor.id, sensorsCfg.get(sensorAltID, sensor.id))

        return sensors


    def pull_and_push_data(self):
        sensors = self.get_sensors()

        while True:
            for sensor in sensors:
                temp = sensor.get_temperature()
                result =self.mqttClient.publish(sensor.topic, temp)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    log.debug(f"Published {temp}°C from Sensor {sensor.id} to {sensor.topic}")
                else:
                    log.error(f"Failed to publish temperature from {sensor.id}")

            self.mqttClient.publish(self.statusTopic, "online")
            time.sleep(self.pollInterval)


    def main(self):
        log.info("Starting onewire-to-mqtt script")

        try:
            self.pull_and_push_data()
        except Exception:
            self.mqttClient.publish(self.statusTopic, "error")
            raise


if __name__ == "__main__":
    OneWireToMQTT().main()
