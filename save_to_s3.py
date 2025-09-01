#!/usr/bin/env python3

import boto3
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

print(AWS_ACCESS_KEY_ID)
print(AWS_SECRET_ACCESS_KEY)
print(AWS_REGION)
print(S3_BUCKET_NAME)

def save_to_s3(data, key_name):
    """
    Save data to S3 bucket
    
    Args:
        data: Data to save (string, bytes, or file path)
        key_name: S3 object key name
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    try:
        if isinstance(data, str) and os.path.isfile(data):
            # If data is a file path
            s3_client.upload_file(data, S3_BUCKET_NAME, key_name)
            print(f"File uploaded successfully: {key_name}")
        else:
            # If data is string or bytes
            if isinstance(data, str):
                data = data.encode('utf-8')
            s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=key_name, Body=data)
            print(f"Data uploaded successfully: {key_name}")
            
    except Exception as e:
        print(f"Error uploading to S3: {e}")

def save_folder_to_s3(folder_path, s3_prefix=""):
    """
    Save all files in a folder to S3 bucket
    
    Args:
        folder_path: Path to the folder to upload
        s3_prefix: S3 key prefix (folder structure in S3)
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        return
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, folder_path)
            s3_key = os.path.join(s3_prefix, relative_path).replace('\\', '/')
            
            try:
                s3_client.upload_file(local_file_path, S3_BUCKET_NAME, s3_key)
                print(f"Uploaded: {local_file_path} -> s3://{S3_BUCKET_NAME}/{s3_key}")
            except Exception as e:
                print(f"Error uploading {local_file_path}: {e}")

if __name__ == "__main__":
    # Upload lineart training data
    save_folder_to_s3("/home/jaxn/DATA/lineart/train", "lineart-training-data")


