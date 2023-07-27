import boto3
import yaml
from dotenv import load_dotenv
load_dotenv()
from io import BytesIO, StringIO
import streamlit as st
import pandas as pd
import os

def create_s3():
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=st.secrets['AWS_ACCESS_KEY'],
            aws_secret_access_key=st.secrets['AWS_SECRET_KEY'],
        )
    except FileNotFoundError:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        )
    return s3

class S3Loader:
    def __init__(self):
        self.bucket = 'cheffrey'
        self.s3 = create_s3()
        
    def load_csv(self, path):
        s3_object = self.s3.get_object(Bucket=self.bucket, Key=path)
        contents = s3_object['Body'].read()
        df = pd.read_csv(BytesIO(contents))
        return df
    
    def write_csv(self, df, path):
        buffer = BytesIO()
        df.to_csv(buffer)
        self.s3.put_object(Body=buffer.getvalue(), Bucket=self.bucket, Key=path)
        return True
    
    def get_all_objects(self, **base_kwargs):
        continuation_token = None
        while True:
            list_kwargs = dict(MaxKeys=1000, **base_kwargs)
            if continuation_token:
                list_kwargs['ContinuationToken'] = continuation_token
            response = self.s3.list_objects_v2(**list_kwargs)
            yield from response.get('Contents', [])
            if not response.get('IsTruncated'):  # At the end of the list?
                break
            continuation_token = response.get('NextContinuationToken')
    
    def load_yaml(self, path):
        obj = self.s3.get_object(Bucket=self.bucket, Key=path)
        return yaml.safe_load(obj['Body'].read())

    def save_yaml(self, obj, path):
        buffer = StringIO()
        yaml.safe_dump(obj, buffer)
        self.s3.put_object(Body=buffer.getvalue(), Bucket=self.bucket, Key=path)
        return True
        