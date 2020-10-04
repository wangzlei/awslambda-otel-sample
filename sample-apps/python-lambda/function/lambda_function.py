import os
import logging
import jsonpickle
import boto3
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()

client = boto3.client('lambda')
client.get_account_settings()

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)
tracer = trace.get_tracer(__name__)

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))
    response = client.get_account_settings()

    with tracer.start_as_current_span("foo"):
        with tracer.start_as_current_span("bar"):
            with tracer.start_as_current_span("baz"):
                print("Hello world, opentelemetry Python")
    return response['AccountUsage']
