# python runtime
FROM python:3.7.2-slim

# working directory
WORKDIR /app
COPY . /app

# install required packages
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# expose http/https ports
EXPOSE 80 443

# env variables: 
# ...

# run app
#CMD ["python", "app.py"]
CMD ["python", "test.py"]

