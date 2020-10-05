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

from wrapt import ObjectProxy, wrap_function_wrapper

from opentelemetry.instrumentation.awslambda.version import __version__
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk.trace import Resource
from opentelemetry.trace import SpanKind, get_tracer

logger = logging.getLogger(__name__)

def _moduleName():
    pass

class AwsLambdaInstrumentor(BaseInstrumentor):
    def _instrument(self, **kwargs):
        _moduleName()
        self._tracer = get_tracer(
            __name__, __version__, kwargs.get("tracer_provider")
        )
        wrap_function_wrapper('lambda_function', 'lambda_handler', self._patched_api_call)

    def _uninstrument(self, **kwargs):
        pass

    def _patched_api_call(self, original_func, instance, args, kwargs):
        with self._tracer.start_as_current_span("LambdaTest", kind=SpanKind.SERVER, ):
            result = original_func(*args, **kwargs)
            return result
