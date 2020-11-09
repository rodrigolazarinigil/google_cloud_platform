from google.cloud import storage
from google.cloud import bigquery
import os
import glob

from google.cloud.bigquery.external_config import HivePartitioningOptions


class GCSFunctions:

    @staticmethod
    def upload_file(bucket_name, source_file_name, destination_blob_name):
        """Uploads a file to the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        print(
            "File {} uploaded to {}.".format(
                source_file_name, destination_blob_name
            )
        )

    @staticmethod
    def get_bucket(bucket_name, project):
        storage_client = storage.Client(project=project)
        return storage_client.get_bucket(bucket_name)

    @classmethod
    def upload_local_directory_to_gcs(cls, local_path, bucket, gcs_path):
        assert os.path.isdir(local_path)
        for local_file in glob.glob(local_path + '/**'):
            if not os.path.isfile(local_file):
                cls.upload_local_directory_to_gcs(local_file, bucket,
                                                  os.path.join(gcs_path, os.path.basename(local_file)))
            else:
                remote_path = os.path.join(
                    gcs_path, local_file[1 + len(local_path):])
                blob = bucket.blob(remote_path)
                blob.upload_from_filename(local_file)


class BigQueryFunctions:

    @staticmethod
    def get_or_create_dataset(
            bq_client: bigquery.Client, dataset_id: str, location: str = "us-west1"
    ) -> bigquery.Dataset:
        """
            Tries to create a dataset in bigquery. If it already exists, just return dataset object
        :param bq_client: Client object to bigquery
        :param dataset_id: Id of the new (of existent) dataset
        :param location: Geographic location in GCP
        :return:
        """
        full_dataset_id = f"{client.project}.{dataset_id}"
        dataset = bigquery.Dataset(full_dataset_id)
        dataset.location = location

        dataset = bq_client.create_dataset(dataset, exists_ok=True, timeout=30)

        return dataset

    @staticmethod
    def create_external_table_hive_partitioning(
            bq_client: bigquery.Client, dataset: bigquery.Dataset, table_id: str, gcs_directory_path: str
    ) -> bigquery.Table:
        """
            Creates an external table with AUTO hive partitioning in GCS
        :param bq_client: Client object to bigquery
        :param dataset: dataset object. Check 'get_or_create_dataset' method
        :param table_id: Table to be created
        :param gcs_directory_path: Directory of GCS with the data. For example:
            If you have a structure like this:
            "gs://bucket/images_metadata/source_id=abc/date=2018-02-20"
            You should pass:
            "gs://bucket/images_metadata"
        :return:
        """
        table = bigquery.Table(dataset.table(table_id))

        external_config = bigquery.ExternalConfig(
            bigquery.SourceFormat.PARQUET
        )
        external_config.source_uris = [f"{gcs_directory_path}/*"]
        hive_part_opt = HivePartitioningOptions()
        hive_part_opt.mode = "AUTO"
        hive_part_opt.source_uri_prefix = gcs_directory_path

        external_config.hive_partitioning = hive_part_opt
        table.external_data_configuration = external_config
        table = bq_client.create_table(table, exists_ok=True)

        return table

    @staticmethod
    def query_estimate(bq_client: bigquery.Client, query: str):
        job_config = bigquery.QueryJobConfig(
            dry_run=True, use_query_cache=False)
        query_job = bq_client.query(query, job_config=job_config)
        print("This query will process {} bytes.".format(
            query_job.total_bytes_processed))


if __name__ == "__main__":
    client = bigquery.Client()
    datasetx = BigQueryFunctions.get_or_create_dataset(
        bq_client=client,
        dataset_id="ds"
    )
    BigQueryFunctions.create_external_table_hive_partitioning(
        bq_client=client,
        dataset=datasetx,
        table_id="table",
        gcs_directory_path="gs://bucket/table"
    )

    BigQueryFunctions.query_estimate(
        bq_client=client,
        query=(
            "select * from `ds.image`"
        )
    )
