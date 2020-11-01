# Copyright 2020, OpenTelemetry Authors
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

# TODO: usage
"""
The opentelemetry-instrumentation-aws-lambda package allows tracing AWS
Lambda function.

Usage
-----

.. code:: python

    import aiohttp
    from opentelemetry.instrumentation.aiohttp_client import (
        AioHttpClientInstrumentor
    )

    # Enable instrumentation
    AioHttpClientInstrumentor().instrument()

    # Create a session and make an HTTP get request
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            await response.text()

API
---
"""

import logging
import os

from wrapt import wrap_function_wrapper
from opentelemetry.instrumentation.aws_lambda.version import __version__
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import SpanKind, get_tracer, get_tracer_provider
from opentelemetry.instrumentation.utils import unwrap

# TODO: aws propagator
from opentelemetry.instrumentation.aws_lambda.tmp.propagator import AWSXRayFormat

logger = logging.getLogger(__name__)

class AwsLambdaInstrumentor(BaseInstrumentor):
    def _instrument(self, **kwargs):
        self._tracer = get_tracer(
            __name__, __version__, kwargs.get("tracer_provider")
        )

        self._tracer_provider = kwargs.get("tracer_provider", get_tracer_provider())

        lambda_handler = os.environ.get("_HANDLER")
        wrapped_names = lambda_handler.split('.')
        self._wrapped_module_name = wrapped_names[0]
        self._wrapped_function_name = wrapped_names[1]

        wrap_function_wrapper(self._wrapped_module_name, self._wrapped_function_name, self._functionPatch)

    # TODO: need to test
    def _uninstrument(self, **kwargs):
        unwrap(self._wrapped_module_name, self._wrapped_function_name)

    def _functionPatch(self, original_func, instance, args, kwargs):
        lambda_context = args[1]
        ctx_invoked_function_arn = lambda_context.invoked_function_arn
        ctx_aws_request_id = lambda_context.aws_request_id
        orig_handler = os.environ.get("ORIG_HANDLER", os.environ.get("_HANDLER"))
        xray_trace_id = os.environ.get('_X_AMZN_TRACE_ID', '')

        propagator = AWSXRayFormat()
        parent_context = propagator.extract(dict.__getitem__, { 'X-Amzn-Trace-Id': xray_trace_id })

        with self._tracer.start_as_current_span(orig_handler, context=parent_context, kind=SpanKind.CLIENT) as span:
            # Refer: https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/semantic_conventions/faas.md#example
            span.set_attribute('faas.execution', ctx_aws_request_id)
            # TODO: faas.id is resource attribute in spec
            span.set_attribute('faas.id', ctx_invoked_function_arn)
            # TODO: aws convension
            span.set_attribute('aws.origin', 'AWS::Lambda:Function')
            
            result = original_func(*args, **kwargs)

        # force_flush before lambda function quit because faas would freeze environment if no new event coming.
        self._tracer_provider.force_flush()

        return result