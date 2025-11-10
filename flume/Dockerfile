FROM eclipse-temurin:8-jdk

# Install dependencies
RUN apt-get update && apt-get install -y wget

# Install Flume
ENV FLUME_VERSION=1.11.0
ENV FLUME_HOME=/opt/flume

RUN wget https://archive.apache.org/dist/flume/${FLUME_VERSION}/apache-flume-${FLUME_VERSION}-bin.tar.gz && \
    tar -xzf apache-flume-${FLUME_VERSION}-bin.tar.gz && \
    mv apache-flume-${FLUME_VERSION}-bin ${FLUME_HOME} && \
    rm apache-flume-${FLUME_VERSION}-bin.tar.gz

RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.2.1/hadoop-common-3.2.1.jar -P ${FLUME_HOME}/lib/ && \
    wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-hdfs/3.2.1/hadoop-hdfs-3.2.1.jar -P ${FLUME_HOME}/lib/ && \
    wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-hdfs-client/3.2.1/hadoop-hdfs-client-3.2.1.jar -P ${FLUME_HOME}/lib/ && \
    wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-auth/3.2.1/hadoop-auth-3.2.1.jar -P ${FLUME_HOME}/lib/

ENV PATH=$PATH:${FLUME_HOME}/bin
ENV JAVA_HOME=/opt/java/openjdk

WORKDIR /opt/flume
CMD ["tail", "-f", "/dev/null"]