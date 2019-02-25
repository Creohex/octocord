# python runtime
FROM python:3.7.2-slim

# working directory
WORKDIR /app
COPY ./requirements.txt /app

# install required packages
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# expose http/https ports
EXPOSE 80 443

# required env variables:
# username, password (local mariadb server)
# ...

VOLUME /certs

# copy webserver files
COPY ./app /app 

# run app
CMD ["python", "app.py"]
#CMD ["python", "test.py"]

