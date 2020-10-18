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

        self._tracer_provider = kwargs.get("tracer_provider")

        lambda_handler = os.environ.get("_HANDLER")
        wrapped_names = lambda_handler.split('.')
        _wrapped_module_name = wrapped_names[0]
        _wrapped_function_name = wrapped_names[1]

        wrap_function_wrapper(_wrapped_module_name, _wrapped_function_name, self._lambdaPatch)

    # TODO: how ?
    def _uninstrument(self, **kwargs):
        pass

    def _lambdaPatch(self, original_func, instance, args, kwargs):
        # instance, kwargs are empty. args[0] event, args[1] lambda context
        self._context_parser(args[1])

        # lambda propagation
        propagator = AWSXRayFormat()
        parent_context = propagator.extract(dict.__getitem__, { 'X-Amzn-Trace-Id': self.xray_trace_id })
        with self._tracer.start_as_current_span(self.lambda_handler, context=parent_context, kind=SpanKind.SERVER) as span:
            # Refer: https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/semantic_conventions/faas.md#example
            span.set_attribute('faas.execution', self.ctx_aws_request_id)
            # TODO: may need an aws convension origin
            span.set_attribute('aws.origin', 'AWS::Lambda:Function')

            # TODO: 'faas.id' is a trouble, cannot be extracted in lambda resource detector
            new_resource = Resource(
                attributes = {
                    'faas.id': self._ctx_invoked_function_arn,
                }
            )
            span.resource = new_resource.merge(span.resource)

            result = original_func(*args, **kwargs)

        # force_flush before lambda function quit
        self._tracer_provider.force_flush()
        logger.info('------- force_flush done --------')
        return result

    def _context_parser(self, lambda_context):
        # logger.info('--- context ---')
        self._ctx_invoked_function_arn = lambda_context.invoked_function_arn
        self.ctx_aws_request_id = lambda_context.aws_request_id

        # logger.info('--- env variables ---')
        # self.lambda_handler = os.environ['_HANDLER']
        self.lambda_handler = os.environ.get("LAMBDA_HANDLER", os.environ.get("_HANDLER"))
        self.xray_trace_id = os.environ.get('_X_AMZN_TRACE_ID', '')
