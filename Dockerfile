 
FROM python:3.8.1 AS base
RUN apt-get update

##################################################

FROM python:3.8.1 AS build
# to suppress some installation warnings
RUN export PATH="$PATH:/root/.local/bin"
RUN python -m pip install --upgrade pip

WORKDIR /opt/build
COPY requirements.txt ./
RUN pip install -r requirements.txt --user

##################################################

FROM base
WORKDIR /opt/app/
ENV PIP_DIR=/root/.local/lib/python3.8/site-packages

COPY iahr ./iahr
COPY exmpl ./exmpl
COPY tests ./tests
COPY .env ./
COPY scripts/docker_entry.sh ./entry.sh

COPY --from=build $PIP_DIR $PIP_DIR

##################################################

ENTRYPOINT ["./entry.sh"]
