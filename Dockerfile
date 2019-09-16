FROM python:3.7-slim
WORKDIR /opt/app
COPY ./ ./
RUN pip install -r requirements.txt
CMD python main.py
