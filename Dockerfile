FROM ubuntu:20.04

RUN apt-get update
RUN apt-get install -y --no-install-recommends sudo python3-mapnik

RUN adduser --disabled-password --gecos '' mapnik
# RUN adduser mapnik sudo && \
#     echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER mapnik
ENV USER=mapnik \
    HOME=/home/mapnik

WORKDIR /home/mapnik
COPY --chown=mapnik *.py /home/mapnik/
COPY --chown=mapnik *.svg /home/mapnik/
COPY --chown=mapnik misc/* /home/mapnik/misc/
COPY --chown=mapnik maps-flags/* /home/mapnik/maps-flags/
