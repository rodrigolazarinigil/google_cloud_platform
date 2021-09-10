## How to prepare your GKE Environment to use workload identity

> Add this config to your cluster (terraform)
```terraform
workload_identity_config {
    identity_namespace = "${var.project}.svc.id.goog"
}
```

> Add this config to your node pool (terraform)
```terraform
workload_metadata_config {
    node_metadata = "GKE_METADATA_SERVER"
}
```

> Create or update a k8s service account with this `annotation` creating a relationship with the GCP service account
```
resource "kubernetes_service_account" "datalake" {
  metadata {
    name = "datalake"
    namespace = var.namespace
    annotations = {
      "iam.gke.io/gcp-service-account" = "datalake-svac@<PROJECTID>.iam.gserviceaccount.com"
    }
  }
  automount_service_account_token = true

  lifecycle {
    ignore_changes = [ secret ]
  }
}
```

> Add a service account binding 
```
resource "google_service_account_iam_binding" "datalake-workload-identity-users" {
  service_account_id = google_service_account.datalake-svac.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:<PROJECTID>.svc.id.goog[${var.namespace}/${kubernetes_service_account.datalake.metadata[0].name}]"
  ]
}
```

> Create a GCP service account 
```
resource "kubernetes_service_account" "datalake" {
  metadata {
    name = "datalake"
    namespace = var.namespace
    annotations = {
      "iam.gke.io/gcp-service-account" = "datalake-svac@<PROJECTID>.iam.gserviceaccount.com"
    }
  }
  automount_service_account_token = true

  lifecycle {
    ignore_changes = [ secret ]
  }
}
```

> Test pod
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: workload-identity-test
  namespace: dataplatform
spec:
  containers:
    - image: google/cloud-sdk:slim
      name: workload-identity-test
      command: ["sleep", "infinity"]
  serviceAccountName: datalake
```

> How to test pod
```sh
kubectl apply -f pod.yaml
kubectl exec -it workload-identity-test gcloud auth list
```
