FROM python:3.12-alpine

RUN pip install pandas fire

RUN pip install git+https://github.com/MrTomRod/get-tax-info

WORKDIR /data
