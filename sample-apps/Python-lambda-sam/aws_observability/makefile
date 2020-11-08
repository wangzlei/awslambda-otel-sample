build-AwsObservability:
	mkdir -p $(ARTIFACTS_DIR)/python
	pip3 install -r requirements.txt -t $(ARTIFACTS_DIR)/python
	cp -r * $(ARTIFACTS_DIR)/python
	rm -rf $(ARTIFACTS_DIR)/python/boto*
	# find $(ARTIFACTS_DIR)/python -name __pycache__ -exec rm -rf  {} \;