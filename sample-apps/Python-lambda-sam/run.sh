#!/bin/bash
TEMPLATE=template.yml
CONFIG=samconfig.toml
# TEMPLATE=template-py37.yml
# CONFIG=samconfig-py37.toml
rm -rf .aws-sam
sam build -u -t $TEMPLATE
find .aws-sam -name __pycache__ -exec rm -rf  {} \;> /dev/null
sam deploy --config-file $CONFIG