import os
import logging
import jsonpickle
import boto3
# import botocore
# import requests
# import sqlite3
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
patch_all()

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)
from opentelemetry.exporter import jaeger
from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter

from opentelemetry.exporter.xraydaemon import XrayDaemonSpanExporter

from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.awslambda import AwsLambdaInstrumentor

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',level=logging.DEBUG)
logger = logging.getLogger()

# resource = Resource(attributes={
#     "service.name": "Sample App"
# })

# trace.set_tracer_provider(TracerProvider(resource=resource))
trace.set_tracer_provider(TracerProvider())

jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name="my-multi-processors",
    agent_host_name="localhost",
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(jaeger_exporter)
)

trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)

otlp_exporter = OTLPSpanExporter(endpoint="localhost:55680")
span_processor = SimpleExportSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)


xrayDaemonSpanExporter = XrayDaemonSpanExporter()
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(xrayDaemonSpanExporter)
)

tracer = trace.get_tracer(__name__)

def lambda_handler(event, context):
    # logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    # logger.info('## EVENT\r' + jsonpickle.encode(event))
    # logger.info('## CONTEXT\r' + jsonpickle.encode(context))

    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)

    return "200 OK"

BotocoreInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())
AwsLambdaInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())
