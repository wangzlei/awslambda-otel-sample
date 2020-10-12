# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os

from wrapt import ObjectProxy, wrap_function_wrapper

import opentelemetry.trace as trace
from opentelemetry.context import Context
from opentelemetry.instrumentation.awslambda.version import __version__
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk.trace import Resource
from opentelemetry.trace import SpanKind, get_tracer

# aws propagator
from opentelemetry.propagator import AWSXRayFormat

logger = logging.getLogger(__name__)

class AwsLambdaInstrumentor(BaseInstrumentor):
    def _instrument(self, **kwargs):
        self._tracer = get_tracer(
            __name__, __version__, kwargs.get("tracer_provider")
        )

        lambda_handler = os.environ['_HANDLER']
        wrapped_names = lambda_handler.split('.')
        _wrapped_module_name = wrapped_names[0]
        _wrapped_function_name = wrapped_names[1]

        wrap_function_wrapper(_wrapped_module_name, _wrapped_function_name, self._lambdaPatch)

    def _uninstrument(self, **kwargs):
        pass

    def _lambdaPatch(self, original_func, instance, args, kwargs):
        # instance, kwargs are empty. args[0] event, args[1] lambda context
        self._context_parser(args[1])

        with self._tracer.start_as_current_span(self.lambda_handler, kind=SpanKind.SERVER, ) as span:

            # TODO: Lambda popagation, refactor after Nathan finish aws propagator
            if self.xray_trace_id and self.xray_trace_id != '':
                logger.info('------ lambda propagation ------')
                propagator = AWSXRayFormat()
                parent_context = propagator.extract(self.xray_trace_id, span.context)           
                #span.context = new_context. TODO: sampled(flag) and trace state
                new_context = trace.SpanContext(
                    trace_id=parent_context.trace_id,
                    span_id=span.context.span_id,
                    trace_flags=trace.TraceFlags(1),
                    trace_state=trace.TraceState(),
                    is_remote=False,
                )
                span.context = new_context
                span.parent = parent_context

            # TODO: another idea, trasparent lambda function segment
            # if self.xray_trace_id and self.xray_trace_id != '':
            #     logger.info('------ trasparent lambda function, like facade ------')
            #     propagator = AWSXRayFormat()
            #     parent_context = propagator.extract(self.xray_trace_id, span.context)           
            #     #span.context = new_context. TODO: sampled(flag) and trace state
            #     span.context = parent_context
            #     span.parent = parent_context


            # Refer: https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/semantic_conventions/faas.md#example
            span.set_attribute('faas.execution', self.ctx_aws_request_id)
            # TODO: may need an aws convension origin
            span.set_attribute('aws.origin', 'AWS::Lambda:Function')

            # TODO: move to lambda resource plugin
            new_resource = Resource(
                attributes = {
                    'cloud.region': self.aws_region,
                    'cloud.provider': 'aws',
                    'faas.name': self.lambda_handler,
                    'faas.id': self._ctx_invoked_function_arn,
                }
            )
            span.resource = new_resource.merge(span.resource)

            result = original_func(*args, **kwargs)
            return result

    def _context_parser(self, lambda_context):
        # logger.info('--- context ---')
        self._ctx_invoked_function_arn = lambda_context.invoked_function_arn
        self.ctx_aws_request_id = lambda_context.aws_request_id
        logger.info(self.ctx_aws_request_id)
        logger.info(self._ctx_invoked_function_arn)

        # logger.info('--- env variables ---')
        self.lambda_handler = os.environ['_HANDLER']
        self.aws_region = os.environ['AWS_REGION']
        self.aws_lambda_function_name = os.environ['AWS_LAMBDA_FUNCTION_NAME']
        self.aws_lambda_log_group_name = os.environ['AWS_LAMBDA_LOG_GROUP_NAME']
        self.aws_lambda_log_stream_name = os.environ['AWS_LAMBDA_LOG_STREAM_NAME']
        self.aws_xray_context_missing = os.environ['AWS_XRAY_CONTEXT_MISSING']
        self.aws_xray_daemon_address = os.environ['AWS_XRAY_DAEMON_ADDRESS']
        self._aws_xray_daemon_address = os.environ['_AWS_XRAY_DAEMON_ADDRESS']
        self._aws_xray_daemon_port = os.environ['_AWS_XRAY_DAEMON_PORT']
        self.xray_trace_id = os.environ.get('_X_AMZN_TRACE_ID', '')


        # logger.info('--- parse module/function ---')
        wrapped_names = self.lambda_handler.split('.')
        self._wrapped_module_name = wrapped_names[0]
        self._wrapped_function_name = wrapped_names[1]

