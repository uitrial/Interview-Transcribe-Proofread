import os
import argparse
from dotenv import load_dotenv
import boto3

def upload_to_s3(folder_path, folder_name):
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve the access key and secret key from environment variables
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Create an S3 client
    s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    # Specify the bucket name
    bucket_name = 'uitrialspeech'

    # Check if the specified folder path exists
    if not os.path.isdir(folder_path):
        print('Invalid folder path.')
        exit()

    # Iterate over the files in the specified folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.mp4'):  # Assuming all videos have the .mp4 extension
            local_file_path = os.path.join(folder_path, filename)
            s3_key = os.path.join(folder_name, filename)

            # Upload the file to S3
            s3_client.upload_file(local_file_path, bucket_name, s3_key)

            print(f'{local_file_path} uploaded to S3 bucket: {bucket_name}/{s3_key}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload videos to AWS S3')
    parser.add_argument('folder_path', type=str, help='Path to the folder containing the videos')
    parser.add_argument('folder_name', type=str, help='Name of the output folder in S3')
    args = parser.parse_args()

    upload_to_s3(args.folder_path, args.folder_name)