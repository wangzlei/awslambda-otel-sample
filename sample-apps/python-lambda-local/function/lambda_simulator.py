import os
from aws_xray_sdk.core import xray_recorder
import json
import logging
from aws_xray_sdk.core.models.trace_header import TraceHeader
# from opentelemetry.propagator.xray_id_generator import AWSXRayIdsGenerator

logger = logging.getLogger(__name__)

# We don't need below in lambda simlator, just an example of real lambda context
# lambdaCtxJson = '{"_epoch_deadline_time_in_ms": 1601956438965, "aws_request_id": "00151111-6838-4eaa-a367-8b79bbb316eb", "client_context": null, "function_name": "python-lambda-function-YI0MC6JQ4BMR", "function_version": "$LATEST", "invoked_function_arn": "arn:aws:lambda:us-east-1:886273918189:function:python-lambda-function-YI0MC6JQ4BMR", "log_group_name": "/aws/lambda/python-lambda-function-YI0MC6JQ4BMR", "log_stream_name": "2020/10/06/[$LATEST]33f5c2beeb3a46dda4e9712885809a22", "memory_limit_in_mb": "128", "py/object": "__main__.LambdaContext"}'
# lambdaCtxDict = json.loads(s=lambdaCtxJson)

# Mock lambda environment variables, except 
envDict = {"AWS_EXECUTION_ENV": "AWS_Lambda_python3.8", "AWS_LAMBDA_FUNCTION_MEMORY_SIZE": "128", "AWS_LAMBDA_FUNCTION_NAME": "python-lambda-function-YI0MC6JQ4BMR", "AWS_LAMBDA_FUNCTION_VERSION": "$LATEST", "AWS_LAMBDA_LOG_GROUP_NAME": "/aws/lambda/python-lambda-function-YI0MC6JQ4BMR", "AWS_LAMBDA_LOG_STREAM_NAME": "2020/10/06/[$LATEST]33f5c2beeb3a46dda4e9712885809a22", "AWS_LAMBDA_RUNTIME_API": "127.0.0.1:9001", "AWS_REGION": "us-east-1", "AWS_XRAY_CONTEXT_MISSING": "LOG_ERROR", "AWS_XRAY_DAEMON_ADDRESS": "localhost:2000", "LAMBDA_RUNTIME_DIR": "/var/runtime", "LAMBDA_TASK_ROOT": "/var/task", "LANG": "en_US.UTF-8", "LD_LIBRARY_PATH": "/var/lang/lib:/lib64:/usr/lib64:/var/runtime:/var/runtime/lib:/var/task:/var/task/lib:/opt/lib", "PATH": "/var/lang/bin:/usr/local/bin:/usr/bin/:/bin:/opt/bin", "PWD": "/var/task", "PYTHONPATH": "/var/runtime", "SHLVL": "0", "TZ": ":UTC", "_AWS_XRAY_DAEMON_ADDRESS": "169.254.79.2", "_AWS_XRAY_DAEMON_PORT": "2000", "_HANDLER": "lambda_function.lambda_handler"}
for k, v in envDict.items():
    os.environ[k] = v

from lambda_function import lambda_handler 

# add env var '_X_AMZN_TRACE_ID' to mock active xray in lambda, will propagate trace from upstream, else lambda function span is root.
def _enable_lambda_propagation():
    logger.info('--- mock active  ---')
    trace_header_str = TraceHeader(
        xray_recorder.current_segment().trace_id,
        xray_recorder.current_segment().id,
        xray_recorder.current_segment().sampled,
    ).to_header_str()
    os.environ['_X_AMZN_TRACE_ID'] = trace_header_str
    

class MockLambdaContext(object):
    pass

# simulate lambda function invocation in local
def main():
    lambdaContext = MockLambdaContext()
    lambdaContext.invoked_function_arn = "arn://sdfasdfasdfas"
    lambdaContext.aws_request_id = "aws_request_id"
    
    # mock a lambda invocation segment
    xray_recorder.begin_segment('AWS::Lambda::Invocation')

    # no lambda propagation if comment out this line, then lambda function span would be root.
    _enable_lambda_propagation()

    # call lambda function
    lambda_handler('mock lambda event', lambdaContext)
    xray_recorder.end_segment()

if __name__ == "__main__":
    main()