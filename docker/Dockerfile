FROM debian

RUN apt-get update && apt-get install -y curl sudo procps

RUN curl -sL "https://raw.githubusercontent.com/gbrian/codx-cli/main/codx.sh" | bash -s
RUN codx nodejs
RUN codx python_311

ENV NVM_DIR="/root/.nvm"
RUN . $NVM_DIR/nvm.sh

EXPOSE 8000
EXPOSE 8001

CMD ["bash", "/app/gpt-web.sh"]