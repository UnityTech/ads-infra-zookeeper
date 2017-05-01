## Zookeeper/Kontrol pod

### Overview

This project is a [**Docker**](https://www.docker.com) image packaging [**Apache Zookeeper 3.4.9**](https://zookeeper.apache.org/) together with [**Kontrol**](https://github.com/UnityTech/ads-infra-kontrol).

It is meant to be included in a [**Kubernetes**](https://github.com/GoogleCloudPlatform/kubernetes) pod.

The container will both run the broker and kontrol. Kontrol runs in in master+slave mode which
means you don't have to deploy a specific control tier to manage your ensemble (e.g it will
automatically self-configure). The broker is managed via a state-machine whose lifecycle include a
periodic health check. Turning the broker on/off is done via a regular supervisor job.

### Configuration

Whenever a topology change is detected the ensemble will be gracefully turned off, re-configured and
turned back on.

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
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: zookeeper
        role: broker
        master: zookeeper.default.svc
    spec:
      containers:
       - image: registry2.applifier.info:5005/ads-infra-zookeeper-alpine-3.5
         name: kontrol
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

---

apiVersion: v1
kind: Service
metadata:
  name: zookeeper
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