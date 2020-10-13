import os
import logging
import jsonpickle
import boto3

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
patch_all()

from opentelemetry import trace
# aws propagator
from opentelemetry.propagator.xray_id_generator import AWSXRayIdsGenerator

from opentelemetry.sdk.resources import (
    Resource,
    OTELResourceDetector,
    get_aggregated_resources,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)

# instrumentor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.awslambda import AwsLambdaInstrumentor

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

from opentelemetry.resource import AwsLambdaResourceDetector
# resource looks weird because get_aggregated_resources has bug, cannot merge _DEFAULT otel attributes
trace.set_tracer_provider(TracerProvider(
    ids_generator=AWSXRayIdsGenerator(), 
    resource=Resource.create().merge(AwsLambdaResourceDetector().detect())),
)
# trace.set_tracer_provider(TracerProvider())



# === jaeger exporter
# from opentelemetry.exporter import jaeger
# jaeger_exporter = jaeger.JaegerSpanExporter(
#     service_name="my-multi-processors",
#     agent_host_name="localhost",
#     agent_port=6831,
# )
# trace.get_tracer_provider().add_span_processor(
#     SimpleExportSpanProcessor(jaeger_exporter)
# )

trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)

# === otlp exporter, collector
# from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter
# otlp_exporter = OTLPSpanExporter(endpoint="localhost:55680")
# span_processor = SimpleExportSpanProcessor(otlp_exporter)
# trace.get_tracer_provider().add_span_processor(span_processor)

# === xray daemon exporter, xray daemon
from opentelemetry.exporter.xraydaemon import XrayDaemonSpanExporter
xrayDaemonSpanExporter = XrayDaemonSpanExporter()
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(xrayDaemonSpanExporter)
)

tracer = trace.get_tracer(__name__)

# Customer's lambda function
def lambda_handler(event, context):
    # logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    # logger.info('## EVENT\r' + jsonpickle.encode(event))
    # logger.info('## CONTEXT\r' + jsonpickle.encode(context))

    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)

    return "200 OK"

# Manual enable otel instrumentation. Can remove them once we package auto-instrumentation into lambda layer.
BotocoreInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())
AwsLambdaInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())
