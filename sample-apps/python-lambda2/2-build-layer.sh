#!/bin/bash
set -eo pipefail
rm -rf package
cd wrapper
pip3 install --target ../package/python -r requirements.txt
rm -rf ../package/python/google/protobuf
rm -rf ../package/python/grpc*
pip3 install --target ../package/tmp --platform=manylinux2014_x86_64 --only-binary=:all: protobuf
pip3 install --target ../package/tmp --platform=manylinux2014_x86_64 --only-binary=:all: grpcio
cp -rf ../package/tmp/* ../package/python/
rm -rf ../package/tmp
cp -r * ../package/python/
rm -rf ../package/python/botocore*
mv ../package/python/lambda_function.py ../function/
cp -r ../../opentelemetry-instrumentation-aws-lambda/src/opentelemetry ../package/python/
find ../package -name __pycache__ -exec rm -rf  {} \;