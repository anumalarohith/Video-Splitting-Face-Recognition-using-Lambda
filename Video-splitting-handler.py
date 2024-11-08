import boto3
import os
import subprocess
import math
import json

#Set up the s3 client
s3 = boto3.client('s3')
def video_splitting_cmdline(video_filename,output_file_name):
    split_cmd = '/opt/ffmpeglib/ffmpeg -i ' +video_filename+ ' -vframes 1 ' + '/tmp/' + f'{output_file_name}'
    try:
        subprocess.check_call(split_cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)

def handler(event, context):	
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
      
    input_filename = f'/tmp/{key}'
      
    file_name = os.path.splitext(os.path.basename(key))[0] + ".jpg"

      # Download the input video file from S3
    s3.download_file(bucket,key, input_filename)

      # Split the video into frames
    video_splitting_cmdline(input_filename,file_name)
    s3.upload_file(os.path.join('/tmp',file_name), f'1226050789-stage-1',file_name)
    payload = {
        'bucket_name': '1226050789-stage-1',
        'file_name': f'{file_name}'
      }
    l= boto3.client('lambda')
    response = l.invoke(
        FunctionName= 'face-recognition',
        InvocationType='Event',  # Invoke asynchronously
        Payload=json.dumps(payload)
    )