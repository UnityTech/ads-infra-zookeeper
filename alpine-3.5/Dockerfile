FROM registry2.applifier.info:5005/ads-infra-kontrol-alpine-3.5:1.1

ENV KONTROL_MODE=master,slave,verbose \
    KONTROL_PAYLOAD=/tmp/state \
    KONTROL_CALLBACK="python /home/kontrol/callback.py" \
    ZOOKEEPER_VERSION=3.4.9

ADD resources/ .
RUN set -ex && \
    apk add --no-cache openjdk8-jre-base bash && \
    apk add --no-cache --virtual .transient gnupg wget && \
    mkdir -p /opt && \
    cd /tmp && \
    wget -q https://www.apache.org/dist/zookeeper/KEYS && \
    wget -q http://mirror.vorboss.net/apache/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/zookeeper-${ZOOKEEPER_VERSION}.tar.gz && \
    wget -q https://www.apache.org/dist/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/zookeeper-${ZOOKEEPER_VERSION}.tar.gz.asc && \
    wget -q https://www.apache.org/dist/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/zookeeper-${ZOOKEEPER_VERSION}.tar.gz.md5 && \
    md5sum -c zookeeper-${ZOOKEEPER_VERSION}.tar.gz.md5 && \
    gpg --import KEYS && \
    gpg --verify zookeeper-${ZOOKEEPER_VERSION}.tar.gz.asc && \
    tar -xzf zookeeper-${ZOOKEEPER_VERSION}.tar.gz -C /opt && \
    mkdir /var/lib/zookeeper-${ZOOKEEPER_VERSION} && \
    chmod +x /home/kontrol/wrapped.sh && \
    mv /home/kontrol/wrapped.sh /opt/zookeeper-${ZOOKEEPER_VERSION}/bin && \
    echo 'hosts: files mdns4_minimal [NOTFOUND=return] dns mdns4' >> /etc/nsswitch.conf && \
    rm -rf /tmp/* && \
    apk del .transient
