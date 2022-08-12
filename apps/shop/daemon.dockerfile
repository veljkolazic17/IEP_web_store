FROM python:3

RUN mkdir -p /opt/src/store
WORKDIR /opt/src/store

# File used for all images
COPY ./configuration.py ./configuration.py
COPY ./models.py ./models.py
COPY ./requirements.txt ./requirements.txt
COPY ./decoraters.py ./decoraters.py
# Only DaEmOn can access these services
COPY ./daemon.py ./daemon.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/store"
ENTRYPOINT ["python", "./daemon.py"]