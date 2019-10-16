### dev version builder ###
FROM snakepacker/python:all as devbuilder
RUN python3.8 -m venv /usr/share/python3/app
ADD requirements*.txt /tmp/
RUN /usr/share/python3/app/bin/pip install --no-cache-dir -Ur /tmp/requirements.txt
RUN /usr/share/python3/app/bin/pip install --no-cache-dir -Ur /tmp/requirements.tests.txt

### dev version ###
FROM snakepacker/python:3.8 as dev
COPY --from=devbuilder /usr/share/python3/app /usr/share/python3/app
ADD api/ /mnt/api
ADD tests/ /mnt/tests
WORKDIR /mnt
ENV PYTHONPATH="/mnt:${PYTHONPATH}"
ENV PATH="/usr/share/python3/app/bin:${PATH}"
ENV FLASK_APP=api

### production version builder ###
FROM snakepacker/python:all as prodbuilder
RUN python3.8 -m venv /usr/share/python3/app
ADD requirements.txt /tmp/
RUN /usr/share/python3/app/bin/pip install --no-cache-dir -Ur /tmp/requirements.txt

### production version ###
FROM snakepacker/python:3.8 as app
COPY --from=prodbuilder /usr/share/python3/app /usr/share/python3/app
ADD api/ /mnt/api
WORKDIR /mnt
ENV PYTHONPATH="/mnt:${PYTHONPATH}"
ENV PATH="/usr/share/python3/app/bin:${PATH}"
ENV FLASK_APP=api
CMD python3 -m flask run --host=0.0.0.0 -p 8080
