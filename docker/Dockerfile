FROM python:3.10-slim

RUN apt-get update \
 && apt-get install -y sudo tk tcl

WORKDIR /app

COPY . .
COPY docker/entrypoint.sh ./entrypoint.sh

RUN pip install --upgrade pip
RUN sudo pip install -e .

CMD ["bash", "/app/entrypoint.sh"]
