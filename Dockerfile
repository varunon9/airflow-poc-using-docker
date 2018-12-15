FROM ubuntu:16.04

# Install python2.7.12
RUN apt-get update && apt-get install -y python python-pip python-dev build-essential

# create airflow home directory
RUN mkdir -p /home/airflow

# set env variable to install GPL dependency
# install from pypi using pip
RUN export AIRFLOW_GPL_UNIDECODE=yes && \
    pip install -U setuptools wheel && \
    pip install apache-airflow

# initialize the database, start the web server and scheduler
CMD airflow initdb && \
    airflow webserver -p 8080 && \
    airflow scheduler