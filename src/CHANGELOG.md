## v1.7.9
### 🚀 Features:

- Added vehicle diagnostics sensors #75. Thanks to @aerrow5!

## v1.7.8
### 🐛 Bug Fixes:

- Fix "Estimated Charging Finish Time" Sensor  

## v1.7.7
### 🚀 Features:

- Added long term statistics for some sensors #68. Thanks to @bogdanbujdea!
- Automatic redact sensitive data from debug log
- Perpare for scheduler option (not yet ready)

## v1.7.6
### 🚀 Features:

- Added support for interior and exterior images via the new [MQTT Image](https://www.home-assistant.io/integrations/image.mqtt/) entity. #62

<b>NOTE: This feature is only available using homeassistant version 2023.7.1 or greater.</b>

## v1.7.5
### 🚀 Features:

- Added support for `LOCKING` and `UNLOCKING` state (Lock entity)

## v1.7.4
### 🐛 Bug Fixes:

- Fixed undocumented charging connection state `CONNECTION_STATUS_FAULT` '#57

## v1.7.3
### 🐛 Bug Fixes:

- Fixed API changes from Volvo #53

<b>ATTENTION: Volvo optimized their API. Maybe you have to set your odometer multiplier to 1. 
Also check all the other multipliers!</b>
## v1.7.2
### 🐛 Bug Fixes:

- Fixed "Engine State" can be "true" or "false", not "RUNNING" or "STOPPED" #47

## v1.7.1
### 🚀 Features:

- Moved "Engine State" from "sensor" to the "binary_sensor" domain
- Improved HA Add-On security level to 7

<b>NOTE: The old "sensor" entity will be not deleted automatically. If you want to clean up your mqtt device, just delete it and restart the volvo2mqtt addon.
</b>

## v1.7.0
### 🚀 Features:

- Added MQTT autodiscovery for HA Add-On users
- Added "Engine State" fallback endpoint for some cars (BEVs)
- Added dynamic icons for "Engine State"
- Turn off the pre-climate switch if "Engine State" changes to "RUNNING"

<b>NOTE: The mqtt broker port is now a string. Just quote your port like this `port: "1883"`</b><br>
<b>NOTE: If you want to switch to MQTT autodiscovery for the HA Add-On change your settings to: <br>
![image](https://i.imgur.com/GBamhFn.png)</b>

## v1.6.5
### 🐛 Bug Fixes:

- Fixed missing key in unit mappings for `en_US` and `en_GB` mapping

## v1.6.4
### 🚀 Features:

- Added dynamic icons for lock, battery and window state #43 

## v1.6.3
### 🚀 Features:

- Moved data source for "Distance to empty" from extended api to connected api

## v1.6.2
### 🚀 Features:

- Moved print statements to logger
- Added more debug logging
- The full HA Addon log can now be found at your addon smb share `\\<Your HA IP>\addons\volvo2mqtt\log\volvo2mqtt.log`

## v1.6.1
### 🚀 Features:

- Added "Washer Fluid Level" and "Distance to Empty" sensors #37 
- Expanded climate control for better state sync with HA

### 🐛 Bug Fixes:

- Fixed wrong return values for not working endpoints
- Fixed app crash on credential renewal timeout #39 

## v1.6.0
### 🚀 Features:

- Added conversion from metric to imperial system for `en_US` and `en_GB` locale
