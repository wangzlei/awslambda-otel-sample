export AOC=$(shell pwd)/aws_observability_collector
export SDK=$(shell pwd)/aws_observability_sdk
build-AwsObservability:
	mkdir -p $(ARTIFACTS_DIR)/python
	pip3 install -r $(SDK)/requirements.txt -t $(ARTIFACTS_DIR)/python
	pip3 install -r $(SDK)/requirements-nodeps.txt -t $(ARTIFACTS_DIR)/tmp --no-deps
	cp -r $(ARTIFACTS_DIR)/tmp/* $(ARTIFACTS_DIR)/python/
	rm -rf $(ARTIFACTS_DIR)/tmp
	cp -r $(SDK)/* $(ARTIFACTS_DIR)/python
	chmod 755 $(ARTIFACTS_DIR)/python/aot-instrument
	rm -rf $(ARTIFACTS_DIR)/python/boto*
	rm -rf $(ARTIFACTS_DIR)/python/urllib3*

	rpm --rebuilddb
	yum install -y go
	mkdir -p $(ARTIFACTS_DIR)/extensions
	cd $(AOC) && go build -o $(ARTIFACTS_DIR)/extensions/aoc-extension *.go
	mkdir -p $(ARTIFACTS_DIR)/otelcol
	cp $(AOC)/config.yaml $(ARTIFACTS_DIR)/otelcol
	cp $(AOC)/aoc_linux_x86_64 $(ARTIFACTS_DIR)/otelcol/collector
	chmod -R 755 $(ARTIFACTS_DIR)/otelcol
