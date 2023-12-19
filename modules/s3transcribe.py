import os
import argparse
import datetime
from dotenv import load_dotenv
import boto3
import time
import re
from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv()

# Retrieve the access key and secret key from environment variables
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
bucket_name = os.getenv('AWS_S3_BUCKET')

# Create a Transcribe client
transcribe_client = boto3.client('transcribe', region_name='eu-central-1', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

# Specify the language code and number of speakers
language_code = 'en-US'
number_of_speakers = 2

def transcribe_from_s3(folder_name):
    # Create a folder with the current timestamp as the folder name
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
    output_folder = f'transcriptions_{timestamp}'

    # List the objects in the specified S3 bucket and folder
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    objects = bucket.objects.filter(Prefix=folder_name)

    # Iterate over the objects and transcribe each video
    for obj in objects:
        if obj.key.endswith('.mp4'):
            video_name = os.path.splitext(os.path.basename(obj.key))[0]
            transcription_file_key = f'{folder_name}/{output_folder}/{video_name}.json'

            # Check if the transcription file already exists
            try:
                s3.Object(bucket_name, transcription_file_key).load()
                print(f'Transcription file already exists for {video_name}. Using existing transcription.')
            except ClientError as e:
                # The file does not exist, proceed with transcription
                if e.response['Error']['Code'] == '404':
                    job_name = f'{video_name}_transcription_{timestamp}'

                    # Configure and start the transcription job
                    try:
                        response = transcribe_client.start_transcription_job(
                            TranscriptionJobName=job_name,
                            LanguageCode=language_code,
                            Media={'MediaFileUri': f's3://{bucket_name}/{obj.key}'},
                            MediaFormat='mp4',
                            Settings={
                                'MaxSpeakerLabels': number_of_speakers,
                                'ShowSpeakerLabels': True
                            },
                            OutputBucketName=bucket_name,
                            OutputKey=transcription_file_key
                        )
                        print(f'Started transcription job: {job_name}')
                    except transcribe_client.exceptions.ConflictException:
                        print(f'Conflict error: Job name {job_name} already exists. Skipping this job.')
                else:
                    # Handle other possible exceptions
                    print(f'Error checking for existing transcription file: {e}')

    # Wait for all transcription jobs to complete
    while True:
        response = transcribe_client.list_transcription_jobs(Status='IN_PROGRESS')
        if len(response.get('TranscriptionJobSummaries', [])) == 0:
            break

        time.sleep(15)  # Wait for 15 seconds

    return f'{folder_name}/{output_folder}'


def download_transcripts(transcribe_folder):
    # Create a local output folder
    os.makedirs(transcribe_folder, exist_ok=True)

    # Create a S3 client
    s3_client = boto3.client('s3', region_name='eu-central-1', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    # List the objects in the specified S3 bucket and folder
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    objects = bucket.objects.filter(Prefix=transcribe_folder)

    # Iterate over the objects and download the transcripts
    for obj in objects:
        if obj.key.endswith('.json'):  # Assuming all JSON files have the .json extension
            output_file = os.path.join(transcribe_folder, os.path.basename(obj.key))
            s3_client.download_file(bucket_name, obj.key, output_file)
            print(f'Downloaded transcription: {output_file}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transcribe videos in S3 bucket')
    parser.add_argument('folder_name', type=str, help='Name of the folder containing videos in S3')
    args = parser.parse_args()

    transcribe_folder = transcribe_from_s3(args.folder_name)
    download_transcripts(transcribe_folder)