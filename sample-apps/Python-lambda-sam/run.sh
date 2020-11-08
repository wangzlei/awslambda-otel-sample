#!/bin/bash
rm -rf .aws-sam
sam build -u -t template-py38.yml
find .aws-sam -name __pycache__ -exec rm -rf  {} \; > /dev/null
sam deploy --config-file samconfig.toml