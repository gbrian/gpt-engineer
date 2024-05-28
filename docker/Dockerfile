FROM debian
ARG GPT_USER_GROUP=1000
ARG GPT_USER=1000

RUN apt-get update && apt-get install -y curl sudo procps python3-full python3-pip python3.11-venv

EXPOSE 8000
EXPOSE 8001

# Add gpt user
RUN [ "${GPT_USER_GROUP}" != "0" ] && groupadd --gid ${GPT_USER_GROUP} gpt || true
RUN [ "${GPT_USER}" != "0" ] && useradd --uid ${GPT_USER} --gid gpt --shell /bin/bash --create-home gpt  || true
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER "${GPT_USER}:${GPT_USER_GROUP}"

WORKDIR /gpt-engineer

COPY ./gpt_engineer /gpt-engineer/gpt_engineer
COPY ./pyproject.toml /gpt-engineer/pyproject.toml
COPY ./gpt-web.sh /gpt-engineer/gpt-web.sh
COPY ./main.py /gpt-engineer/main.py

ENV VENV_PATH=/gpt-engineer/.venv
ENV PATH ${VENV_PATH}:${PATH}
RUN rm  /usr/lib/python3.11/EXTERNALLY-MANAGED
RUN python3 -m venv ${VENV_PATH}
RUN pip3 install -e .
# RUN cd gpt_engineer/api/client_chat && npm i

RUN curl -sL "https://raw.githubusercontent.com/gbrian/codx-cli/main/nodejs.sh" | bash -s

CMD ["bash", "/gpt-engineer/gpt-web.sh"]