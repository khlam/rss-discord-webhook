FROM ghcr.io/khlam/py/py:3.8
WORKDIR /app/
COPY ./main.py /app/main.py
RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev cargo
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev cargo && \
    pip install cryptography && \
    pip install feedparser && \
    pip install xmltodict && \
    apk del gcc musl-dev python3-dev libffi-dev openssl-dev cargo
ENTRYPOINT ["python3", "main.py"]