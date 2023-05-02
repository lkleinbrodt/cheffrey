import streamlit as st
import os
import pandas as pd
from io import BytesIO, StringIO
import boto3
import yaml
from dotenv import load_dotenv

load_dotenv()
S3_BUCKET = "cheffrey"


def create_s3():
    """
    Create a boto3 s3 client to access AWS S3 buckets.

    Returns:
        client(clientobj): boto3 s3 client

    Raises:
        FileNotFoundError: The secrets file containing AWS_ACCESS_KEY and AWS_SECRET_KEY wasn't found.

    Example:
        >>> s3_client = create_s3()"""
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
            aws_secret_access_key=st.secrets["AWS_SECRET_KEY"],
        )
    except FileNotFoundError:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        )
    return s3


s3 = create_s3()


def load_s3_csv(key, s3=s3):
    """
    Load a CSV file from an S3 bucket into a pandas dataframe.

    Args:
        key (str): The key (path and filename) of the csv file in the S3 bucket.
        s3 (boto3.S3.Client, optional): The boto3 s3 client to use. Defaults to the s3 client instance.

    Returns:
        pandas.DataFrame: A pandas dataframe containing the contents from the CSV file in S3 bucket.
    """
    s3_object = s3.get_object(Bucket=S3_BUCKET, Key=key)
    contents = s3_object["Body"].read()
    df = pd.read_csv(BytesIO(contents))
    return df


def save_s3_csv(df, key, s3=s3):
    """
    Save a pandas DataFrame in CSV format to Amazon S3.

    Args:
        df (pandas.DataFrame): The DataFrame to be saved in CSV format.
        key (str): The S3 key where the file will be saved.
        s3 (boto3.client, optional): The `boto3.client` instance from which to connect to Amazon S3.
                                     Defaults to `s3`.

    Returns:
        bool: Returns `True` if the file was sucessfully saved to S3.
    """
    buffer = BytesIO()
    df.to_csv(buffer)
    s3.put_object(Body=buffer.getvalue(), Bucket=S3_BUCKET, Key=key)
    return True


def get_all_s3_objects(s3=s3, **base_kwargs):
    """
    Return a generator that yields all the objects in an Amazon S3 bucket.

    Keyword arguments:
    s3 -- an instance of Boto3 S3 Client to interact with S3 service.
    **base_kwargs -- any additional arguments to be passed to S3 client's list_objects_v2() method.

    The generator recursively yields objects in the S3 bucket until there are no more objects left.
    The default MaxKeys set to 1000 can be overridden by providing the function with a value for the 'MaxKeys' argument.
    """
    continuation_token = None
    while True:
        list_kwargs = dict(MaxKeys=1000, **base_kwargs)
        if continuation_token:
            list_kwargs["ContinuationToken"] = continuation_token
        response = s3.list_objects_v2(**list_kwargs)
        yield from response.get("Contents", [])
        if not response.get("IsTruncated"):
            break
        continuation_token = response.get("NextContinuationToken")


def load_s3_yaml(key, s3=s3):
    """
    Load a YAML file from S3 and return a dictionary.

    Args:
        key (str): Name of the key/file on S3.
        s3 (Boto3 S3Client, optional): S3 client. Defaults to s3.

    Returns:
        dict: A dictionary created by loading the YAML file on S3.

    Raises:
        botocore.exceptions.ClientError: If the specified key was not found.
    """
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    return yaml.safe_load(obj["Body"].read())


def save_s3_yaml(obj, key, s3=s3):
    """
    Safely dumps a YAML string into StringIO buffer before putting it into a specified s3 bucket using a specified key.

    Args:
        obj (object): The obj to store.
        key (string): The s3 key to use when storing the object
        s3 (botocore.client.S3): The s3 resource to use.

    Returns:
        bool: `True` if the object was stored successfully, `False` otherwise."""
    buffer = StringIO()
    yaml.safe_dump(obj, buffer)
    s3.put_object(Body=buffer.getvalue(), Bucket=S3_BUCKET, Key=key)
    return True
