FROM python:3

RUN mkdir -p /opt/src/store
WORKDIR /opt/src/store

# File used for all images
COPY ./configuration.py ./configuration.py
COPY ./models.py ./models.py
COPY ./requirements.txt ./requirements.txt
COPY ./decoraters.py ./decoraters.py
# Only warehouse manager can access these services
COPY ./warehouse.py ./warehouse.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/store"
ENTRYPOINT ["python", "./warehouse.py"]