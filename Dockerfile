FROM cgr.dev/chainguard/wolfi-base:latest

ARG USER_UID=1000
ARG HOME_DIR=/opt/app

RUN apk add --no-cache python-3.12 py3.12-pip tini &&\
    addgroup -g $USER_UID app &&\
    adduser -D -u $USER_UID -G app -h ${HOME_DIR} app &&\
    chown -R app:app /opt/app

WORKDIR ${HOME_DIR}

USER app

# Copy the application code
COPY --chown=1000:1000 --chmod=750 . .

RUN python -m venv /opt/app/deploy &&\
    source /opt/app/deploy/bin/activate &&\
    pip install --no-cache -r requirements.txt

EXPOSE 8000
ENV TINI_SUBREAPER=1
ENV MCP_HTTP_PORT=8000
ENV MCP_HTTP_HOST=0.0.0.0


ENTRYPOINT [ "/usr/bin/tini", "-g", "--", "/opt/app/entrypoint.sh" ]

CMD ["uvicorn", "--port", "8000", "--host", "0.0.0.0", "main:app", "--app-dir", "/opt/app"]