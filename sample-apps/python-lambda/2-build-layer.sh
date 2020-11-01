#!/bin/bash
set -eo pipefail
rm -rf package
cd wrapper
pip3 install --target ../package/python -r requirements.txt
cp -r * ../package/python/
rm -rf ../package/python/botocore*
mv ../package/python/lambda_function.py ../function/