# onewire-to-mqtt
Publish onewire sensor data to a MQTT Broker

# Setup
## via Container (e.g. Docker)
1. copy the [compose.yaml](https://raw.githubusercontent.com/Glopix/onewire-to-mqtt/refs/heads/main/compose.yaml) file from this repo and save it.
2. copy the [config.ini](https://raw.githubusercontent.com/Glopix/onewire-to-mqtt/refs/heads/main/config.ini) file from this repo and save it.
3. Edit the config.ini according to your requirements. Pay particular attention to the `host`, `port`, `tls`, `username` and `password` settings in the `[mqtt]` section. Remove the settings for the `username` and `password` if your mqtt broker does not require them.
4. run `docker compose up` and watch the output for errors.
5. If not errors occur, restart the containers by pressing `ctrl` + `c` and run `docker compose up -d`
## without Container
1. copy the [onewire-to-mqtt.py](https://github.com/Glopix/onewire-to-mqtt/blob/main/onewire-to-mqtt.py) file from this repo and save it.
2. copy the [config.ini](https://raw.githubusercontent.com/Glopix/onewire-to-mqtt/refs/heads/main/config.ini) file from this repo and save it.
3. Edit the config.ini according to your requirements. Pay particular attention to the `host`, `port`, `tls`, `username` and `password` settings in the `[mqtt]` section. Remove the settings for the `username` and `password` if your mqtt broker does not require them.
4. Install the required python packages from [requirements.txt](https://github.com/Glopix/onewire-to-mqtt/blob/main/requirements.txt)
5. run `./onewire-to-mqtt.py` watch the output for errors.
6. 5 If no errors occur, configure the script to run at computer startup, e.g. via cron or by configuring it as a service.

