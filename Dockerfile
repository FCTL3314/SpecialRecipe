FROM python:3.11-alpine

WORKDIR /usr/src/SpecialRecipe

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . .

RUN pip install --upgrade pip && pip install -r requirements/production.txt

RUN chmod a+x entrypoint.sh
