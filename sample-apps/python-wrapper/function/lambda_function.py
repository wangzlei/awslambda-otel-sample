import sys
import os
import logging
import jsonpickle
import boto3
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)
BotocoreInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('lambda')
client.get_account_settings()

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))
    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        logger.info(bucket.name)

    return response['AccountUsage']


