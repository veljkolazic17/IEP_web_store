FROM python:3

RUN mkdir -p /opt/src/store
WORKDIR /opt/src/store

# File used for all images
COPY ./configuration.py ./configuration.py
COPY ./models.py ./models.py
COPY ./requirements.txt ./requirements.txt
COPY ./decoraters.py ./decoraters.py
# Only admin can access these services
COPY ./migrate.py ./migrate.py
COPY ./manage.py ./manage.py
COPY ./admin.py ./admin.py
COPY ./start.sh ./start.sh

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/store"
ENTRYPOINT ["./start.sh"]