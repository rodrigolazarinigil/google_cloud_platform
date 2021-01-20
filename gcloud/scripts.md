## Gcloud commands

List gcloud existent roles:
```sh
gcloud iam roles list | grep pubsub
```

Delete GCP service account:
```sh
gcloud iam service-accounts delete datalake-pubsub@neuralmed-datalake-prod.iam.gserviceaccount.com
```

List service account:
```
gcloud iam service-accounts list                                     
```

Login as user:
```
gcloud auth login
```                                             

Create key for service account:
```
gcloud iam service-accounts keys create ~/Credentials/file.json --iam-account <servaccount>@<project>.iam.gserviceaccount.com
```