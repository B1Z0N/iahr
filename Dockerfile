FROM python:3.8.1 AS base
RUN apt-get update && apt-get install --no-install-recommends -y ffmpeg

FROM python:3.8.1 AS build
WORKDIR /opt/build
COPY ./requirements.txt ./
RUN pip install -r requirements.txt --user

FROM base
WORKDIR /opt/app
ENV PIP_DIR=/root/.local/lib/python3.8/site-packages
COPY ./ ./
COPY --from=build $PIP_DIR $PIP_DIR
RUN mkdir -p sessions/
CMD python main.py
