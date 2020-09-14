export BASE_SPACE=$(shell pwd)
export BUILD_SPACE=$(BASE_SPACE)/build
export AOC_BOOTSTRAP=$(BUILD_SPACE)/aoc-extension
export S3_BUCKET_NAME=aoc-layers
export AOC_LAYER_NAME=my-aoc-layer

clean:
	rm -rf build/

build:
	@echo Building bootstrap
	mkdir -p $(BUILD_SPACE)
	GOOS=linux GOARCH=amd64 go build -o $(AOC_BOOTSTRAP) main.go

package:
	@echo Package zip file for aoc Lambda layer
	mkdir -p $(BUILD_SPACE)/extensions
	cp $(AOC_BOOTSTRAP) $(BUILD_SPACE)/extensions/
	mkdir -p $(BUILD_SPACE)/otelcol
	touch $(BUILD_SPACE)/preview-extensions-ggqizro707
	cp config.yaml $(BUILD_SPACE)/otelcol
	wget -O $(BUILD_SPACE)/otelcol/collector https://github.com/open-telemetry/opentelemetry-collector-contrib/releases/download/v0.9.0/otelcontribcol_linux_amd64
	cd $(BUILD_SPACE) && zip -r otel-col-extension.zip preview-extensions-ggqizro707 otelcol extensions

publish-layer: clean build package
	@echo Publishing aoc Lambda layer
	aws s3 mb s3://$(S3_BUCKET_NAME)
	aws s3 cp $(BUILD_SPACE)/otel-col-extension.zip s3://$(S3_BUCKET_NAME)
	aws lambda publish-layer-version --layer-name $(AOC_LAYER_NAME) --content S3Bucket=$(S3_BUCKET_NAME),S3Key=otel-col-extension.zip