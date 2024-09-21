import os
import boto3

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '.aws\credentials.txt'

s3 = boto3.client('s3')

# List all buckets
try:
    response = s3.list_buckets()
    print("Existing buckets:")
    for bucket in response['Buckets']:
        print(f"  {bucket['Name']}")
except Exception as e:
    print(f"Error: {e}")
