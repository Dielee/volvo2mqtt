ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache python3 bash py3-pip

# set the working directory in the container
WORKDIR /volvoAAOS2mqtt

# download requirements.txt
RUN wget https://raw.githubusercontent.com/Dielee/volvo2mqtt/main/requirements.txt

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY / .

# command to run on container start
CMD [ "python", "-u", "./main.py" ]
