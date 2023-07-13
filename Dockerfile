FROM python:3.11
ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

ENV PYTHONPATH=/var/project/

WORKDIR /var/project
COPY requirements.txt /var/project/
RUN pip install -r requirements.txt --no-cache-dir
RUN python -m spacy download en_core_web_sm
COPY ./ /var/project/

