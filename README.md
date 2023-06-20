# Volvo2Mqtt

This component establishes a connection between the newer AAOS Volvo cars and Home Assistant via MQTT.<br>
Maybe this component works also with other Volvo cars. Please try out the native Volvo [integration](https://www.home-assistant.io/integrations/volvooncall/) before using this component! If the native component doesn't work for your car, try this mqtt bridge.

## Confirmed working with
- Volvo XC40 BEV (2023)
- V60 T8 PHEV (2023)

Please let me know if your car works with this addon so I can expand the list!

## Setup

Just install this addon with the following command.
Please note to fill in your settings inside the environment variables.

`docker run --pull=always -e CONF_updateInterval=300 -e CONF_babelLocale='de' -e CONF_mqtt='@json {"broker": "", "username": "", "password": ""}' -e CONF_volvoData='@json {"username": "", "password": "", "vin": "", "vccapikey": ""}' -e TZ='Europe/Berlin' --name volvo2mqtt ghcr.io/dielee/volvo2mqtt:latest`

Here is what every option means:

| Name                 |   Type    |   Default    | Description                                                     |
| -------------------- | :-------: | :----------: | --------------------------------------------------------------- |
| `updateInterval`     | `int`     | **required** | Update intervall in seconds.                                     |
| `babelLocale`        | `string`  | **required** | Select your country from this [list](https://www.ibm.com/docs/en/radfws/9.7?topic=overview-locales-code-pages-supported). "Locale name" is the column you need!                                        |
| `mqtt`               | `json`    | **required** | Broker = Mqtt Broker IP / Username and Passwort are optional!   |
| `volvoData`          | `json`    | **required** | Username and password are REQUIRED. Car vin can be a single vin or a list of multiple vins like `["vin1", "vin2"]`. If no vin is provided, <b>ALL</b> of your vehicles will be used. Vccapi key is REQUIRED. Get your Vccapi key from [here](https://developer.volvocars.com/account/).                                   |
| `TZ`                 | `string`  |              | Container timezone eg "Europe/Berlin" |
| `debug`              | `string`  |              | Debug option (True/False) - optional! |

If you like my work:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U7U8MFXCF)
