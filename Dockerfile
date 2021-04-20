 
FROM python:3.8.1 AS base
RUN apt-get update
RUN apt-get install -y inotify-tools

##################################################

FROM python:3.8.1 AS build
# to suppress some installation warnings
ENV PATH="/root/.local/bin:${PATH}"
RUN python -m pip install --upgrade pip

WORKDIR /opt/app
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt --user

##################################################

FROM BASE
WORKDIR /opt/app
ENV PIP_DIR=/root/.local/lib/python3.8/site-packages
COPY .env ./.env

COPY --from=build $PIP_DIR $PIP_DIR

##################################################

ENV PYTHONPATH="/opt/app/:$PYTHONPATH" 
ENTRYPOINT ["./scripts/docker_entry.sh"]