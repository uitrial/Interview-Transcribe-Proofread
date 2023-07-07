from modules import s3upload, s3transcribe, parse
import argparse

if __name__ == "__main__":
    # Create Argument Parser
    parser = argparse.ArgumentParser(description='Process video, create transcripts, proofread with OpenAI GPT4.')
    parser.add_argument('input_folder', type=str, help='Input folder with .mp4 videos')
    parser.add_argument('s3_folder', type=str, help='Output folder name in S3 bucket')
    args = parser.parse_args()

    # Step 1: Upload videos to S3
    print("Step 1: Uploading videos to S3...")
    s3upload.upload_to_s3(args.input_folder, args.s3_folder)

    # Step 2: Transcribe videos from S3 and download the transcriptions
    print("Step 2: Transcribing videos from S3 and downloading the transcriptions...")
    transcribe_folder = s3transcribe.transcribe_from_s3(args.s3_folder)
    s3transcribe.download_transcripts(transcribe_folder)

    # Step 3: Parse transcriptions
    print("Step 3: Parsing transcriptions...")
    parse.proofread_transcripts(transcribe_folder)

    print("Finished processing videos! View the resulting transcript and .docx file in the timestamped folder.")