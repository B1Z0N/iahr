FROM python:3.8
WORKDIR /opt/app
COPY ./ ./
RUN apt-get install -y libmagickwand-dev
RUN pip install -r requirements.txt
CMD python main.py
