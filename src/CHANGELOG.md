## v1.8.25
### 🚀 Features:

- Fix INTERNAL_SERVER_ERROR #165

## v1.8.24
### 🚀 Features:

- Add option for dynamic interval settings #160
- Add warnings endpoint #151

## v1.8.23
### 🚀 Features:

- Add new charging system states #152

## v1.8.22
### 🚀 Features:

- Change units to HA default #148

## v1.8.21
### 🐛 Bug Fixes:

- Try to fix addon build #146

## v1.8.20
### 🐛 Bug Fixes:

- Fix Addon crash if icon state is `UNKOWN`
- Add `UNSPECIFIED` state for windows


## v1.8.19
### 🐛 Bug Fixes:

- Fix Estimated Charging Time not changing to zero #133 

## v1.8.18
### 🐛 Bug Fixes:

- Fix Backend State Sensor returning `null`

## v1.8.17
### 🚀 Features:

- Move vehicle and vehicle details to v2 endpoint

### 🐛 Bug Fixes:

- Fix Battery Charge Level icon update

## v1.8.16
### 🚀 Features:

- Add `Average energy consumption`, `Distance to empty battery` and `Washer fluid level` sensors
- Support force update for `Backend state` Sensor
- Use cached requests for fuel endpoint

## v1.8.15
### 🚀 Features:

- Move `batteryChargeLevel` to the new v2 fuel endpoint
- Add api backend status sensor

## v1.8.14
### 🐛 Bug Fixes:

- Fix distance to empty sensor #127
- Remove unused service warning trigger sensor

## v1.8.13
### 🐛 Bug Fixes:

- Add "Time to Service" sensor #125<p>
  <b>Breaking change: The "Months to Service" sensor will be automatically deleted.<br>
  "Time to Service" contains this information now.

## v1.8.12
### 🐛 Bug Fixes:

- Fix `AJAR` state for windows
- Fix deprecation from `currentThread` to `current_thread`

## v1.8.11
### 🐛 Bug Fixes:

- Remove old code from checks for running engine sensor
- Move battery charge level sensor from v2 to v1, as v2 returns 404

## v1.8.10
### 🐛 Bug Fixes:

- Add `AJAR` state for sunroof #123

## v1.8.9
### 🐛 Bug Fixes:

- Fix api changes from volvo #121

## v1.8.8
### 🐛 Bug Fixes:

- Fix json decode error, if volvo API returns a simple string #104

## v1.8.7
### 🚀 Features:

- Add option to disable log completely #96 

### 🐛 Bug Fixes:

- Fix regex error for some mailaddresses #97

## v1.8.6
### 🚀 Features:

- Add option to use multiple docker containers (with different logins) #93

## v1.8.5
### 🚀 Features:

- Allow phone number as username #91

## v1.8.4
### 🚀 Features:

- Optimize Addon configuration #90

## v1.8.3
### 🚀 Features:

- Add `device_class: battery` for battery state sensors from BEV and PHEV 

## v1.8.2
### 🚀 Features:

- Add `updateInterval` limit to prevent abuse (60 Seconds)
- Add `vccapikey` limit to prevent abuse (3 Keys)
- Optimize vcc api key change behaviour

## v1.8.1
### 🐛 Bug Fixes:

- Fix app crash if `debug` is not set #86

## v1.8.0
### 🚀 Features:

- <b>Breaking change: The `vccapikey` setting is now a list. It is possible to
  add multiple VCCAPIKEYs. This will be helpful if you are extending your 10.000 call limit sometimes.
  Change your vccapikey config like this:
  
  Old:
  ```
    "vccapikey": "vccapikey1" 
  ```

  New:
  ```
    vccapikey:
      - vccapikey1
      - vccapikey2
      - vccapikey3
      - etc.
  ```
  More information about this feature [here](https://github.com/Dielee/volvo2mqtt/issues/84).
    </b>

## v1.7.10
### 🐛 Bug Fixes:

- Fix application startup if using `en_US` or `en_GB` as locale

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
