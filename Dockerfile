FROM python:3.13-alpine

WORKDIR /app


RUN apk update
RUN apk upgrade
RUN rm -rf /var/cache/apk/*

COPY . .
RUN sh install.sh




# Switch to non-root user
USER appuser

CMD ["python", "setup.py"]