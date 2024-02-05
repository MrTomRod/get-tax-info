FROM python:3.12-alpine

RUN apk update
RUN apk add git
RUN pip install pandas fire

RUN pip install git+https://github.com/MrTomRod/get-tax-info

# Download NCBI and BUSCO data
RUN get-tax-info taxid-to-busco-dataset --taxid 110

WORKDIR /data

# podman build . --tag taxid-tools:latest
# podman save --format oci-archive taxid-tools:latest -o taxid-tools.tar
# apptainer build taxid-tools.sif oci-archive://taxid-tools.tar
# ./taxid-tools.sif get-tax-info taxid-to-busco-dataset --taxid 110
