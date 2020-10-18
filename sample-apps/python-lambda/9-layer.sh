#!/bin/bash
export S3_BUCKET_NAME=otel-layers

set -eo pipefail
rm -rf package
pip3 install --target package/python -r function/requirements.txt
cp -r function/* package/python/
rm package/python/lambda_function.py
rm package/python/requirements.txt

zip -r otel-ai-python.zip package
# aws s3api get-bucket-location --bucket ${S3_BUCKET_NAME} --output-template-file out.yml || aws s3 mb s3://${S3_BUCKET_NAME} --output-template-file out.yml
# aws s3 cp otel-ai-python.zip s3://${S3_BUCKET_NAME}
# aws lambda publish-layer-version --layer-name otel-ai-python --content S3Bucket=${S3_BUCKET_NAME},S3Key=otel-ai-python.zip --compatible-runtimes python3.6 python3.7 python3.8