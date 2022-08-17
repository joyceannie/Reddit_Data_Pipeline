import boto3
import botocore
import configparser
import pathlib
import sys
from validation import validate_input

# Read Configuration File
parser = configparser.ConfigParser()
script_path = pathlib.Path(__file__).parent.resolve()
config_file = "configuration.conf"
parser.read(f"{script_path}/{config_file}")

#Configuration variables
BUCKET_NAME = parser.get('aws_config', 'bucket_name')
AWS_REGION = parser.get('aws_config', 'aws_region')

try:
    output_name = sys.argv[1]
except Exception as e:
    print(f"Command line argument not passed. Error {e}")
    sys.exit(1)
    
#S3 variable
FILENAME = f'{output_name}.csv'
KEY = FILENAME

def main():
    """
    upload csv data to S3 bucket
    """
    validate_input(output_name)
    s3_conn = get_s3_connection()
    create_s3_bucket(s3_conn)
    upload_data(s3_conn)
    
    
def get_s3_connection():
    try:
        s3 = boto3.resource('s3')
        return s3
    except Exception as e:
        print(f'Unable to connect to S3. Error: {e}')
        sys.exit(1)

def create_s3_bucket(s3_conn):
    '''
    Create the bucket if it doesn't exist
    '''
    exists = True
    try:
        s3_conn.meta.client.head_bucket(Bucket=BUCKET_NAME)
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = e.response['Error']['Code']
        if error_code == '404':
            exists = False
    if not exists:
        s3_conn.create_bucket(
            bucket = BUCKET_NAME,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )

def upload_data(s3_conn):
    '''
    Upload csv file to the S3 bucket
    '''
    s3_conn.meta.client.upload_file(
        Filename="/tmp/" + FILENAME, Bucket=BUCKET_NAME, Key=KEY
    )

if __name__ =="__main__":
    main()