# Volvo2Mqtt

This component establishes a connection between the newer AAOS Volvo cars and Home Assistant via MQTT.<br>
Maybe this component works also with other Volvo cars. Please try out the native Volvo [integration](https://www.home-assistant.io/integrations/volvooncall/) before using this component! If the native component doesn't work for your car, try this mqtt bridge.

## Confirmed working with
- XC40 BEV (2023)
- V60 T8 PHEV (2023)
- C40 PHEV (2023)
- XC90 T8 PHEV (2023)

Please let me know if your car works with this addon so I can expand the list!

## Supported features
- Lock/unlock car
- Start/stop climate
- Sensor "Battery Charge Level"
- Sensor "Electric Range"
- Sensor "Charging System Status"
- Sensor "Estimated Charging Finish Time"
- Multiple cars

NOTE: Energy status currently available only for cars in the Europe / Middle East / Africa regions. [source](https://developer.volvocars.com/apis/energy/v1/overview/#availability)

## Setup
Docker:

Just install this addon with the following command.
Please note to fill in your settings inside the environment variables.

`docker run --pull=always -e CONF_updateInterval=300 -e CONF_babelLocale='de' -e CONF_mqtt='@json {"broker": "", "username": "", "password": ""}' -e CONF_volvoData='@json {"username": "", "password": "", "vin": "",   "vccapikey": ""}' -e TZ='Europe/Berlin' --name volvo2mqtt ghcr.io/dielee/volvo2mqtt:latest`

HA Add-On<br>

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FDielee%2Fvolvo2mqtt)

Here is what every option means:

| Name                 |   Type    |   Default    | Description                                                     |
| -------------------- | :-------: | :----------: | --------------------------------------------------------------- |
| `CONF_updateInterval`     | `int`     | **required** | Update intervall in seconds.                                     |
| `CONF_babelLocale`        | `string`  | **required** | Select your country from this [list](https://www.ibm.com/docs/en/radfws/9.7?topic=overview-locales-code-pages-supported). "Locale name" is the column you need!                                        |
| `CONF_mqtt`               | `json`    | **required** | Broker = Mqtt Broker IP / Username and Passwort are optional!   |
| `CONF_volvoData`          | `json`    | **required** | Username and password are REQUIRED. Car vin can be a single vin or a list of multiple vins like `["vin1", "vin2"]`. If no vin is provided, <b>ALL</b> of your vehicles will be used. Vccapi key is REQUIRED. Get your Vccapi key from [here](https://developer.volvocars.com/account/).                                   |
| `CONF_debug`              | `string`  |              | Debug option (true/false) - optional! |
| `TZ`                 | `string`  |              | Container timezone eg "Europe/Berlin" |

If you like my work:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U7U8MFXCF)
