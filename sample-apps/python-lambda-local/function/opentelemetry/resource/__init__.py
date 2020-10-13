import os
from opentelemetry.sdk.resources import (
    Resource,
    ResourceDetector,
)

class AwsLambdaResourceDetector(ResourceDetector):
    def detect(self) -> "Resource":
        lambda_handler = os.environ['_HANDLER']
        aws_region = os.environ['AWS_REGION']
        env_resource_map = {
            'cloud.region': aws_region,
            'cloud.provider': 'aws',
            'faas.name': lambda_handler,
            # faas.id is in lambda context, hard to be extract in the beginning.
            # 'faas.id': self._ctx_invoked_function_arn,
        }
        return Resource(env_resource_map)
