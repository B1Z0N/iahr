FROM python:3.8 as build
WORKDIR /opt/build
COPY ./requirements.txt ./
RUN pip install -r requirements.txt --user

FROM python:3.8
WORKDIR /opt/app
COPY ./ ./
COPY --from=build \
  /root/.local/lib/python3.8/site-packages \
  /root/.local/lib/python3.8/site-packages
RUN mkdir -p sessions/
CMD python main.py
