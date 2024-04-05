FROM debian
ARG GPT_USER_GROUP=1000
ARG GPT_USER=1000

RUN apt-get update && apt-get install -y curl sudo procps python3-full python3-pip python3.11-venv

RUN curl -sL "https://raw.githubusercontent.com/gbrian/codx-cli/main/codx.sh" | bash -s
RUN codx nodejs

ENV NVM_DIR="/root/.nvm"
RUN . $NVM_DIR/nvm.sh

EXPOSE 8000
EXPOSE 8001

WORKDIR /gpt-engineer
COPY . . 

ENV VENV_PATH=/gpt-engineer/.venv
ENV PATH $VENV_PATH:$PATH
RUN rm  /usr/lib/python3.11/EXTERNALLY-MANAGED
RUN python3 -m venv $VENV_PATH
RUN pip3 install -e .
# RUN cd gpt_engineer/api/client_chat && npm i

# Add gpt user
RUN groupadd --gid $GPT_USER_GROUP gpt;
RUN useradd --uid $GPT_USER --gid gpt --shell /bin/bash --create-home gpt;
USER gpt

CMD ["bash", "/app/gpt-web.sh"]