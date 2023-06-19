# Volvo2Mqtt

This component establishes a connection between the newer AAOS Volvo cars and Home Assistant via MQTT.<br>
Maybe this component works also with other Volvo cars. Please try out the native Volvo [integration](https://www.home-assistant.io/integrations/volvooncall/) before using this component! If the native component doesn't work for your car, try this mqtt bridge.

## Setup

Just install this addon with the following command.
Please note to fill in your settings inside the environment variables.

`docker run -e CONF_updateInterval=300 -e CONF_babelLocale='de' -e CONF_mqtt='@json {"broker": "", "username": "", "password": ""}' -e CONF_volvoData='@json {"username": "", "password": "", "vin": "", "vccapikey": ""}' -e TZ='Europe/Berlin' --name volvo2mqtt ghcr.io/dielee/volvo2mqtt:latest`

Here is what every option means:

| Name                 |   Type    |   Default    | Description                                                     |
| -------------------- | :-------: | :----------: | --------------------------------------------------------------- |
| `updateInterval`     | `int`     | **required** | Updateintervall in seconds.                                     |
| `babelLocale`        | `string`  | **required** | Locale for date Format                                          |
| `mqtt`               | `json`    | **required** | Broker = Mqtt Broker IP / Username and Passwort are optional!   |
| `volvoData`          | `json`    | **required** | Username and password are required. Car vin can be a single vin or a list of multiple vins like `["vin1", "vin2"]`. If no vin is provided, <b>ALL</b> of your vehicles will be used. Vccapi key is your api key from [here](https://developer.volvocars.com/account/).                                   |
| `TZ`                 | `string`  |              | Container timezone eg "Europe/Berlin" |

If you like my work:

<a href="https://www.buymeacoffee.com/dielee" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>
