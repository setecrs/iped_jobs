from kubernetes import client, config
import requests
import yaml
import datetime

class K8s:
  def __init__(self, namespace="default"):
    self.namespace = namespace
    config.load_kube_config()

  def addJob(self, image, IPEDJAR, EVIDENCE_PATH, OUTPUT_PATH, IPED_PROFILE, ADD_ARGS, ADD_PATHS, **env):
    job = _addJob(image, IPEDJAR, EVIDENCE_PATH, OUTPUT_PATH, IPED_PROFILE, ADD_ARGS, ADD_PATHS, **env)
    v1job : client.V1Job = client.BatchV1Api().create_namespaced_job(self.namespace, job)
    return v1job.metadata.name

def _addJob(image, IPEDJAR, EVIDENCE_PATH, OUTPUT_PATH, IPED_PROFILE, ADD_ARGS, ADD_PATHS, **env):
  job = yaml.safe_load(f"""---
apiVersion: batch/v1
kind: Job
metadata:
  name: ipedworker-{datetime.datetime.now():%Y%m%d-%H%M%S-%f}
spec:
  backoffLimit: 0 # 0 = no retries
  template:
    metadata:
      labels:
        app: ipedworker
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - ipedworker
            topologyKey: "kubernetes.io/hostname"
      containers:
        - name: main
          image: {image}
          command: ["/worker-go/overwrite_profile.sh", "/worker-go/worker-go"]
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
          readinessProbe:
            httpGet:
              path: /readiness
              port: http
          env:
          - name: LOCK_URL
            value: http://$(LOCKER_SERVICE_HOST):$(LOCKER_SERVICE_PORT)
          - name: NOTIFY_URL
            value: http://$(WEKAN_NOTIFIER_SERVICE_HOST):$(WEKAN_NOTIFIER_SERVICE_PORT)
          - name: IPEDJAR
            value: {IPEDJAR}
          - name: EVIDENCE_PATH
            value: {EVIDENCE_PATH}
          - name: OUTPUT_PATH
            value: {OUTPUT_PATH}
          - name: IPED_PROFILE
            value: {IPED_PROFILE}
          - name: ADD_ARGS
            value: {ADD_ARGS}
          - name: ADD_PATHS
            value: {ADD_PATHS}
          volumeMounts:
            - mountPath: /mnt/ipedtmp
              name: ipedtmp
            - mountPath: /mnt/cloud/operacoes
              name: operacoes
            - mountPath: /operacoes
              name: operacoes
            - mountPath: /mnt/led
              name: led
            - mountPath: /mnt/kff
              name: kff
            - mountPath: /mnt/PhotoDNA
              name: photodna
            - mountPath: /worker-go
              name: worker
          resources:
            limits:
              cpu: 16
              memory: 64Gi
            requests:
              cpu: 16
              memory: 64Gi
      volumes:
        - name: ipedtmp
          hostPath:
            path: /mnt/ipedtmp/
            type: Directory
        - name: worker
          cephfs:
            monitors:
            - 192.168.2.42:6789
            path: /k8s/worker-go
            secretRef:
              name: ceph-secret
            user: admin
        - name: ipedprofiles
          cephfs:
            monitors:
            - 192.168.2.42:6789
            path: /iped_profiles/
            secretRef:
              name: ceph-secret
            user: admin
        - name: operacoes
          cephfs:
            monitors:
            - 192.168.2.42:6789
            path: /operacoes/
            secretRef:
              name: ceph-secret
            user: admin
        - name: led
          cephfs:
            monitors:
            - 192.168.2.42:6789
            path: /led/V1.25.01
            secretRef:
              name: ceph-secret
            user: admin
        - name: kff
          cephfs:
            monitors:
            - 192.168.2.42:6789
            path: /kff/iped-kff-1.2
            secretRef:
              name: ceph-secret
            user: admin
        - name: photodna
          cephfs:
            monitors:
            - 192.168.2.42:6789
            path: /PhotoDNA
            secretRef:
              name: ceph-secret
            user: admin

      restartPolicy: Never
      """)
  envlist = []
  for k,v in env.items():
    envlist.append(dict(name=k, value=v))
  job['spec']['template']['spec']['containers'][0]['env'] += envlist
  return job
