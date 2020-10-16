import os
import logging
import jsonpickle
import boto3

# Customer's lambda function
def lambda_handler(event, context):
    # logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    # logger.info('## EVENT\r' + jsonpickle.encode(event))
    # logger.info('## CONTEXT\r' + jsonpickle.encode(context))

    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)

    return "200 OK"

