FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication
# Files required to run app
COPY ./app.py ./app.py
COPY ./configuration.py ./configuration.py
COPY ./models.py ./models.py
COPY ./decoraters.py ./decoraters.py
COPY ./manage.py ./manage.py
COPY ./migrate.py ./migrate.py
COPY ./password_utils.py ./password_utils.py
COPY ./requirements.txt ./requirements.txt
COPY ./start.sh ./start.sh
RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/authentication"

ENTRYPOINT ["./start.sh"]
