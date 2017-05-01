#!/bin/sh

export ZOO_LOG_DIR=/var/log
export ZOO_LOG4J_PROP="INFO, ROLLINGFILE"
export JAVA_OPTS="-Xms2g\
-Xmx2g\
-Xloggc:/var/log/GC.log\
-XX:+UseCompressedOops\
-XX:+UseParNewGC\
-XX:+UseConcMarkSweepGC\
-XX:+CMSClassUnloadingEnabled\
-XX:+CMSScavengeBeforeRemark\
-XX:+DisableExplicitGC\
-XX:+UnlockDiagnosticVMOptions\
-XX:ParGCCardsPerStrideChunk=4096\
-XX:+PrintGCDateStamps\
-XX:+PrintGCDetails\
-XX:+UseGCLogFileRotation\
-XX:NumberOfGCLogFiles=4\
-XX:GCLogFileSize=25M\
-XX:+HeapDumpOnOutOfMemoryError\
-XX:HeapDumpPath=/var/log/heap.hprof\
-Dfile.encoding=UTF-8\
-Dzookeeper.log.dir=/var/log\
-Dzookeeper.root.logger=INFO, ROLLINGFILE"

/opt/zookeeper-3.4.9/bin/zkServer.sh start-foreground