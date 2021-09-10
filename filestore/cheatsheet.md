## Filestore cheatsheet 

> Creating the filestore
```sh
gcloud filestore instances create datalake-filestore \
    --project=<PROJECT> \
    --location=us-west1-b \
    --tier=STANDARD \
    --file-share=name="files",capacity=1TB \
    --network=name="<VPCNAME>" \
    --labels=application=datalake
```

> Create filestore Persistence Volume
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: fileserver
spec:
  capacity:
    storage: 1T
  accessModes:
  - ReadWriteMany
  nfs:
    path: /files
    server: <FilestoreInstanceIP>
```

> Create filestore Persistence Volume Claim
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: fileserver-claim
spec:
  # Specify "" as the storageClassName so it matches the PersistentVolume's StorageClass.
  # A nil storageClassName value uses the default StorageClass. For details, see
  # https://kubernetes.io/docs/concepts/storage/persistent-volumes/#class-1
  accessModes:
  - ReadWriteMany
  storageClassName: ""
  volumeName: fileserver
  resources:
    requests:
      storage: 1T
```

> Rsync
```sh
gsutil -m rsync -r gs://bucket/tmp/ct_testing/ /opt/filestore/
```

> Find instance IP
```sh
gcloud filestore instances describe datalake-filestore --zone us-west1-b | sed -n '/ipAddresses/{n;p;}'
```

> Delete filestore instace
```sh
gcloud filestore instances delete datalake-filestore --zone us-west1-b 
```

> Test pod
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: dataplatform
spec:
  containers:
    - name: container-name
      image: google/cloud-sdk:slim
      volumeMounts:
        - mountPath: /opt/filestore
          name: mypvc
      command: ["sleep", "infinity"]
  serviceAccountName: datalake
  volumes:
    - name: mypvc
      persistentVolumeClaim:
        claimName: datalake-fileserver-claim
        readOnly: false
```
