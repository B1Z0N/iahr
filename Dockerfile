FROM python:3.8.1 as build
WORKDIR /opt/build
COPY ./requirements.txt ./
RUN pip install -r requirements.txt --user

FROM python:3.8.1
WORKDIR /opt/app
ENV PIP_DIR=/root/.local/lib/python3.8/site-packages
COPY ./ ./
COPY --from=build $PIP_DIR $PIP_DIR
RUN mkdir -p sessions/
RUN apt-get update && \
  apt-get --no-install-recommends install -y ffmpeg
CMD python main.py
