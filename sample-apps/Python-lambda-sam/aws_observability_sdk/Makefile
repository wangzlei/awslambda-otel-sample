build-AwsObservabilitySdk:
	mkdir -p $(ARTIFACTS_DIR)/python
	pip3 install -r requirements.txt -t $(ARTIFACTS_DIR)/python
	pip3 install -r requirements-nodeps.txt -t $(ARTIFACTS_DIR)/tmp --no-deps
	cp -r $(ARTIFACTS_DIR)/tmp/* $(ARTIFACTS_DIR)/python/
	rm -rf $(ARTIFACTS_DIR)/tmp
	cp -r * $(ARTIFACTS_DIR)/python
	chmod 755 $(ARTIFACTS_DIR)/python/aot-instrument
	rm -rf $(ARTIFACTS_DIR)/python/boto*
	rm -rf $(ARTIFACTS_DIR)/python/urllib3*

	rpm --rebuilddb
	yum install -y go wget
	mkdir -p $(ARTIFACTS_DIR)/extensions
	go build -o $(ARTIFACTS_DIR)/extensions/aoc-extension main.go
	mkdir -p $(ARTIFACTS_DIR)/otelcol
	cp config.yaml $(ARTIFACTS_DIR)/otelcol
	cp aoc_linux_x86_64 $(ARTIFACTS_DIR)/otelcol/collector
	chmod -R 755 $(ARTIFACTS_DIR)/otelcol
