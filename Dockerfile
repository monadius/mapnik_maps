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


# FROM ubuntu:22.04

# RUN cd /home/mapnik && \
#     git clone --depth 1 https://github.com/mapnik/mapnik.git && \
#     cd mapnik && \
#     git submodule update --depth 1 --init

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     git cmake \
#     python3 python-is-python3 \
#     g++ \
#     libboost-dev libboost-regex-dev libboost-filesystem-dev libboost-system-dev \
#     libz-dev \
#     libicu-dev \
#     libproj-dev \
#     libpng-dev \
#     libharfbuzz-dev