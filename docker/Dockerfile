FROM debian
ARG GPT_USER_GROUP=1000
ARG GPT_USER=1000

RUN apt-get update && apt-get install -y git curl sudo procps python3-full python3-pip python3.11-venv

RUN rm  /usr/lib/python3.11/EXTERNALLY-MANAGED

EXPOSE 8000
EXPOSE 8001

# Add gpt user
RUN [ "${GPT_USER_GROUP}" != "0" ] && groupadd --gid ${GPT_USER_GROUP} gpt || true
RUN [ "${GPT_USER}" != "0" ] && useradd --uid ${GPT_USER} --gid gpt --shell /bin/bash --create-home gpt  || true
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN curl -fsSL https://deb.nodesource.com/setup_22.x -o nodesource_setup.sh
RUN bash nodesource_setup.sh
RUN apt-get install -y nodejs
RUN npm install -g yarn
RUN node -v

USER "${GPT_USER}:${GPT_USER_GROUP}"

WORKDIR /gpt-engineer

COPY --chown=gpt ./gpt_engineer /gpt-engineer/gpt_engineer
COPY --chown=gpt ./notebooks /gpt-engineer/notebooks
COPY --chown=gpt ./pyproject.toml /gpt-engineer/pyproject.toml
COPY --chown=gpt ./gpt-web.sh /gpt-engineer/gpt-web.sh
COPY --chown=gpt ./main.py /gpt-engineer/main.py

RUN pip install -e .

ENV PATH=$PATH:/home/gpt/.local/bin

CMD ["bash", "/gpt-engineer/gpt-web.sh"]