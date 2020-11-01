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

from unittest.mock import Mock, patch

from opentelemetry.instrumentation.aws_lambda import AwsLambdaInstrumentor
from opentelemetry.test.test_base import TestBase
from opentelemetry import trace

class TestAwsLambdaInstrumentor(TestBase):
    """AWS Lambda Instrumentation integration testsuite"""

    def setUp(self):
        super().setUp()
        AwsLambdaInstrumentor().instrument()

    def tearDown(self):
        super().tearDown()
        AwsLambdaInstrumentor().uninstrument()

    def test_null(self):
        pass