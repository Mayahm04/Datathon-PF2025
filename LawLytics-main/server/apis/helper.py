import boto3


class Helper:
    def __init__(self):
        self.data_bucket_name = "rag-data-pf-2025"
        self.s3_client = boto3.client('s3')

    def sendDataToBucket(self, source: str, file_path: str):
        s3_folder = source
        file_name = file_path
        s3_object_name = f'{s3_folder}/{file_name}'
        self.s3_client.upload_file(file_name, self.data_bucket_name, s3_object_name)


helper = Helper()