#!/bin/bash

install_sf(){

    apk --no-cache update
    apk --no-cache add bash curl gcc wget mysql-client openssl-dev
    apk --no-cache add python36-dev libffi-dev musl-dev py3-virtualenv

    # get binary zip from nexus - vfc-nfvo-genericparser

    wget -q -O modeling-genericparser.zip "https://nexus.onap.org/service/local/artifact/maven/redirect?r=snapshots&g=org.onap.modeling.genericparser&a=modeling-genericparser&e=zip&v=${pkg_version}-SNAPSHOT&e=zip" && \
    unzip modeling-genericparser.zip && \
    rm -rf modeling-genericparser.zip && \
    pip install --upgrade setuptools pip  && \
    pip install --no-cache-dir --pre -r  /service/modeling/genericparser/requirements.txt
}

add_user(){

    apk --no-cache add sudo
    addgroup -g 1000 -S onap && \
    adduser onap -D -G onap -u 1000 && \
    chmod u+w /etc/sudoers && \
    sed -i '/User privilege/a\\onap    ALL=(ALL:ALL) NOPASSWD:ALL' /etc/sudoers && \
    chmod u-x /etc/sudoers && \
    sudo chown onap:onap -R /service
}

config_logdir(){

    if [ ! -d "/var/log/onap" ]; then
       sudo mkdir /var/log/onap
    fi

    sudo chown onap:onap -R /var/log/onap
    chmod g+s /var/log/onap

}

clean_sf_cache(){

    rm -rf /var/cache/apk/*
    rm -rf /root/.cache/pip/*
    rm -rf /tmp/*
}

install_sf
wait
add_user
config_logdir
clean_sf_cache



