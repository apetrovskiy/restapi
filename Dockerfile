### production version ###
FROM snakepacker/python:all
RUN python3.8 -m venv /usr/share/python3/app
COPY requirements.txt /tmp/
RUN /usr/share/python3/app/bin/pip install --no-cache-dir --disable-pip-version-check -r /tmp/requirements.txt

FROM snakepacker/python:3.8 as prod
COPY --from=0 /usr/share/python3/app /usr/share/python3/app
COPY api/ /opt/restapi/api
WORKDIR /opt/restapi
ENV PATH="/usr/share/python3/app/bin:${PATH}"
CMD gunicorn -b 0.0.0.0:8080 "api:create_app()"

### dev version ###
FROM snakepacker/python:all
COPY --from=0 /usr/share/python3/app /usr/share/python3/app
COPY requirements.tests.txt /tmp/
RUN /usr/share/python3/app/bin/pip install --no-cache-dir --disable-pip-version-check -r /tmp/requirements.tests.txt

FROM snakepacker/python:3.8 as dev
COPY --from=2 /usr/share/python3/app /usr/share/python3/app
COPY api/ /opt/restapi/api
COPY tests/ /opt/restapi/tests
WORKDIR /opt/restapi
ENV PATH="/usr/share/python3/app/bin:${PATH}"
ENV FLASK_APP=api
ENV FLASK_ENV=development
CMD pylama && \
    mypy --ignore-missing-imports api tests && \
    coverage run --source api -m pytest && \
    coverage report -m  && \
    python -m flask run --host=0.0.0.0 -p 8080
