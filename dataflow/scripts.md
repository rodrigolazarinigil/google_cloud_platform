## Executing job on dataflow

After creating the apache beam pipeline in a python file, call this to deploy and run the job on GCP:
```sh
python "${PYTHON_FILE_NAME}".py \
    --project="${PROJECT_NAME}" \
    --output_path=gs://"${BUCKET_NAME}"/dataflow_output \
    --region="${REGION}" \
    --job_name=testdataflow \
    --runner="${RUNNER}"Runner \
    --streaming \
    --staging_location gs://"${BUCKET_NAME}"/staging_location \
    --temp_location=gs://"${BUCKET_NAME}"/temp
```

If you ran the code above with the "template" parameter, you can trigger a new job with "gcloud":
```sh
gcloud dataflow jobs run "${JOB_NAME}"  \
    --gcs-location gs://${BUCKET_NAME}/${FILE_PATH}.py \
    --region "${REGION}" \
    --staging-location gs://${BUCKET_NAME}/temp
```

Example running "wordcount.py":

```sh
python dataflow/wordcount.py \
    --project=${PROJECT_NAME} \
    --region=${REGION} \
    --runner=${RUNNER}Runner \
    --output gs://${BUCKET_NAME}/output \
    --staging_location gs://${BUCKET_NAME}/staging_location \
    --temp_location=gs://${BUCKET_NAME}/temp \
    [--service_account_email=]
```