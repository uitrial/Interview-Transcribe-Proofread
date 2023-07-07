
# Project Title

This is a script to automate Interview transcription and proofreading and transcript formatting into .docx. Uses AWS Transcribe, S3, and OpenAI API (GPT3.5). 
## Installation

Python 3.10+

```bash
  pip3 install -r requirements.txt
```
    
## Usage/Examples

```bash
usage: process_transcripts.py [-h] input_folder s3_folder

positional arguments:
  input_folder  Input folder with .mp4 videos
  s3_folder     Output folder name in S3 bucket

e.g:

python3 process_transcripts.py /Users/kvyb/Documents/Uitrial_Interviews testing_proofread
```


## Features

- Uploads .mp4 2-speaker video to S3
- Transcribes speaker voices into text
- Proofreads the transcribed text, improving quality
- Formats the text into a .docx format


## Feedback

If you have any feedback, please reach out to me.

Note:
- Only supports .mp4
- Still needs a quick manual proof-read, especially regarding names.



![Uitrial TMS Badge](https://img.shields.io/badge/TMS-Uitrial-1972F5)


