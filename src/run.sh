#!/command/with-contenv bashio
export IS_HA_ADDON="true"

export MQTTHOST=$(bashio::services mqtt "host")
export MQTTPORT=$(bashio::services mqtt "port")
export MQTTUSER=$(bashio::services mqtt "username")
export MQTTPASS=$(bashio::services mqtt "password")

python -u main.py