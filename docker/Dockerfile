FROM nexus3.onap.org:10001/onap/integration-python:8.0.0

ARG USER=etsicatalog \
	GROUP=etsicatalog \
	UID=1000 \
	GID=1000 \
	PKG_VERSION

ENV http_proxy=$HTTP_PROXY \ 
	https_proxy=$HTTPS_PROXY \
	pkg_version=$PKG_VERSION

#Copying files (based on assembly.xml)
ADD . /service/modeling/etsicatalog/
WORKDIR /service/modeling/etsicatalog

#Installing dependencies, setting permissions, cleaning up
USER root
RUN apk --no-cache add curl gcc wget mysql-client openssl-dev python3-dev libffi-dev musl-dev py3-virtualenv && \
    	pip install --upgrade setuptools pip  && \
        pip install --no-cache-dir --pre -r requirements.txt && \
	addgroup -g $GID -S $GROUP && \
	adduser $USER -D --system --disabled-password --no-create-home --shell /bin/false -G $GROUP -u $UID && \ 
	chown $USER:$GROUP -R /service && \
	chown $USER:$GROUP -R /var/log/onap && \
	find  /service -name '*.sh'|xargs chmod a+x && \
	chmod g+s /var/log/onap && \
	rm -rf /var/cache/apk/* && \
	rm -rf /root/.cache/pip/* && \
	rm -rf /tmp/*

EXPOSE 8806

USER $USER
ENTRYPOINT docker/docker-entrypoint.sh
