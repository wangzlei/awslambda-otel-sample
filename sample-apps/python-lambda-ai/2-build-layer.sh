#!/bin/bash
export S3_BUCKET_NAME=otel-layers
set -eo pipefail
rm -rf package
pip3 install --target package/python -r function/requirements.txt
cp -r function/* package/python
rm package/python/lambda_function.py
rm package/python/requirements.txt

zip -r otel-ai-python.zip function
aws s3 mb s3://$(S3_BUCKET_NAME)
aws s3 cp $(BUILD_SPACE)/otel-col-extension.zip s3://$(S3_BUCKET_NAME)
aws lambda publish-layer-version --layer-name otel-ai-python.zip --content S3Bucket=$(S3_BUCKET_NAME),S3Key=otel-ai-python.zip --compatible-runtimes python3.6 python3.7 python3.8