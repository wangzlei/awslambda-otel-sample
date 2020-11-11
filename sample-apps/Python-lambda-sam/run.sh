#!/bin/bash
TEMPLATE=template.yml
CONFIG=samconfig.toml
# TEMPLATE=template-py37.yml
# CONFIG=samconfig-py37.toml
rm -rf .aws-sam
rm -rf aws_observability_collector
mkdir aws_observability_collector && cp -r ../../extensions/aoc-extension/* aws_observability_collector
# remove local cp if aoc lambda is ready
cp /Users/wangzl/workspace/aws-ob/aws-otel-collector/build/linux/aoc_linux_x86_64 aws_observability_collector
sam build -u -t $TEMPLATE
find .aws-sam -name __pycache__ -exec rm -rf  {} \;
sam deploy --config-file $CONFIG