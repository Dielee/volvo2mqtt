ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache python3 bash py3-pip

# set the working directory in the container
WORKDIR /volvoAAOS2mqtt

# download requirements.txt
RUN wget --no-cache https://raw.githubusercontent.com/Dielee/volvo2mqtt/main/requirements.txt

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY / .
RUN chmod a+x /volvoAAOS2mqtt/run.sh

# command to run on container start
CMD [ "/volvoAAOS2mqtt/run.sh" ]