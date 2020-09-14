BASE_SPACE=$(pwd)
BUILD_SPACE=${BASE_SPACE}/build
S3_BUCKET_NAME=aoc-layers
AOC_LAYER_NAME=my-java-otel-layer

echo "Starting..."

echo "Package Lambda layer file"
rm -rf build/
mkdir -p ${BUILD_SPACE}/javaagent
wget -O ${BUILD_SPACE}/javaagent/otelagent.jar https://github.com/anuraaga/aws-opentelemetry-java-instrumentation/releases/download/v0.9.0-alpha.1/aws-opentelemetry-agent.jar
cd ${BUILD_SPACE} && zip -r my-javaagent.zip javaagent

echo "Publishing..."
aws s3 mb s3://${S3_BUCKET_NAME}
aws s3 cp ${BUILD_SPACE}/my-javaagent.zip s3://${S3_BUCKET_NAME}
aws lambda publish-layer-version --layer-name ${AOC_LAYER_NAME} --content S3Bucket=${S3_BUCKET_NAME},S3Key=my-javaagent.zip

echo "Done"