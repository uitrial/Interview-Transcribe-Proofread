import os
import argparse
import datetime
from dotenv import load_dotenv
import boto3
import time

# Load environment variables from .env file
load_dotenv()

# Retrieve the access key and secret key from environment variables
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# Create a Transcribe client
transcribe_client = boto3.client('transcribe', region_name='eu-central-1', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

# Specify the language code and number of speakers
language_code = 'en-US'
number_of_speakers = 2

def transcribe_from_s3(folder_name):
    # Create a folder with the current timestamp as the folder name
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_folder = f'transcriptions_{timestamp}'

    # List the objects in the specified S3 bucket and folder
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('uitrialspeech')
    objects = bucket.objects.filter(Prefix=folder_name)

    # Iterate over the objects and transcribe each video
    for obj in objects:
        if obj.key.endswith('.mp4'):  # Assuming all videos have the .mp4 extension
            video_name = os.path.splitext(os.path.basename(obj.key))[0]
            job_name = f'{video_name}_transcription_{timestamp}'

            # Configure the transcription job
            response = transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                LanguageCode=language_code,
                Media={'MediaFileUri': f's3://uitrialspeech/{obj.key}'},
                MediaFormat='mp4',
                Settings={
                    'MaxSpeakerLabels': number_of_speakers,
                    'ShowSpeakerLabels': True
                },
                OutputBucketName='uitrialspeech',  # Specify your S3 bucket where the transcriptions will be stored
                OutputKey=f'{folder_name}/{output_folder}/{video_name}.json'  # Specify the output folder and filename
            )

            print(f'Started transcription job: {job_name}')

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
    bucket = s3.Bucket('uitrialspeech')
    objects = bucket.objects.filter(Prefix=transcribe_folder)

    # Iterate over the objects and download the transcripts
    for obj in objects:
        if obj.key.endswith('.json'):  # Assuming all JSON files have the .json extension
            output_file = os.path.join(transcribe_folder, os.path.basename(obj.key))
            s3_client.download_file('uitrialspeech', obj.key, output_file)
            print(f'Downloaded transcription: {output_file}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transcribe videos in S3 bucket')
    parser.add_argument('folder_name', type=str, help='Name of the folder containing videos in S3')
    args = parser.parse_args()

    transcribe_folder = transcribe_from_s3(args.folder_name)
    download_transcripts(transcribe_folder)