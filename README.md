## Apache Zookeeper+Kontrol pod

### Overview

This project is a [**Docker**](https://www.docker.com) image packaging
[**Apache Zookeeper 3.4.9**](https://zookeeper.apache.org/) together with
[**Kontrol**](https://github.com/UnityTech/ads-infra-kontrol). It is meant
to be included in a [**Kubernetes**](https://github.com/GoogleCloudPlatform/kubernetes)
pod.

The container will both run the JVM broker as well as its control tier: *kontrol* runs
in master+slave mode which means you don't have to deploy a specific tier to manage your
ensemble (e.g just deploy 1+ pods and they will automatically self-configure). Each broker
JVM is managed via a state-machine which is transitioned in the *kontrol* callback.

### Lifecycle

Turning the JVM on/off is done via a regular supervisor job. If a broker fails
(e.g is not serving requests anymore) the automaton will attempt to re-start it.
The health check is performed via a simple MNTR command issued locally. The
broker JVM will not be started until we get a first *kontrol* callback.

Whenever a topology change is detected the ensemble will be gracefully turned off,
re-configured and turned back on. This happens in a rolling fashion.

### Building the image

Pick a distro and build from the top-level directory. For instance:

```
$ docker build -f alpine-3.5/Dockerfile .
```

### Manifest

```
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: zookeeper
  namespace: test
spec:
  replicas: 5
  template:
    metadata:
      labels:
        app: zookeeper
        role: broker
      annotations:
        kontrol.unity3d.com/master: zookeeper.test.svc
    spec:
      containers:
       - image: registry2.applifier.info:5005/ads-infra-zookeeper-alpine-3.5
         name: zookeeper
         imagePullPolicy: Always
         ports:
         - containerPort: 2181
           protocol: TCP
         - containerPort: 2888
           protocol: TCP
         - containerPort: 3888
           protocol: TCP
         - containerPort: 8000
           protocol: TCP
         env:
          - name: NAMESPACE
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace

---

apiVersion: v1
kind: Service
metadata:
  name: zookeeper
  namespace: test
spec:
  ports:
  - protocol: TCP
    port: 2181
  - protocol: TCP
    port: 8000
  selector:
    app: zookeeper
    role: broker
```

### Support

Contact olivierp@unity3d.com for more information about this project.