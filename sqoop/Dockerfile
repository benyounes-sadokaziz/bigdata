FROM bde2020/hadoop-base:2.0.0-hadoop3.2.1-java8

# Fix Debian Stretch repositories (moved to archive)
RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list && \
    sed -i '/stretch-updates/d' /etc/apt/sources.list && \
    apt-get update -o Acquire::Check-Valid-Until=false && \
    apt-get install -y wget curl && \
    rm -rf /var/lib/apt/lists/*

ENV SQOOP_VERSION=1.4.7
ENV SQOOP_HOME=/opt/sqoop

RUN wget --no-check-certificate https://archive.apache.org/dist/sqoop/${SQOOP_VERSION}/sqoop-${SQOOP_VERSION}.bin__hadoop-2.6.0.tar.gz && \
    tar -xzf sqoop-${SQOOP_VERSION}.bin__hadoop-2.6.0.tar.gz && \
    mv sqoop-${SQOOP_VERSION}.bin__hadoop-2.6.0 ${SQOOP_HOME} && \
    rm sqoop-${SQOOP_VERSION}.bin__hadoop-2.6.0.tar.gz

RUN wget --no-check-certificate https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.28/mysql-connector-java-8.0.28.jar && \
    cp mysql-connector-java-8.0.28.jar ${SQOOP_HOME}/lib/ && \
    rm mysql-connector-java-8.0.28.jar

# Download commons-lang library (required for Sqoop)
RUN wget --no-check-certificate https://repo1.maven.org/maven2/commons-lang/commons-lang/2.6/commons-lang-2.6.jar && \
    cp commons-lang-2.6.jar ${SQOOP_HOME}/lib/ && \
    rm commons-lang-2.6.jar

ENV PATH=$PATH:${SQOOP_HOME}/bin
ENV HADOOP_COMMON_HOME=/opt/hadoop-3.2.1
ENV HADOOP_MAPRED_HOME=/opt/hadoop-3.2.1

RUN echo "export HADOOP_COMMON_HOME=/opt/hadoop-3.2.1" >> ${SQOOP_HOME}/conf/sqoop-env.sh && \
    echo "export HADOOP_MAPRED_HOME=/opt/hadoop-3.2.1" >> ${SQOOP_HOME}/conf/sqoop-env.sh

WORKDIR /opt/sqoop
CMD ["tail", "-f", "/dev/null"]