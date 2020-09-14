# awslambda-otel-sample
make sure you have aws lambda extensions api trial permission, config aws credencial and aws regions as us-east-1
1. run `1-create-bucket.sh`
2. run `2-deploy.sh`
3. run `3-invoke.sh`

Then can get traces in region us-west-2

This sample relys on 2 Lambda layers: aws-otel-auto-instrumentation and otel-collector, now opentelemetry collector config is hardcode as below, will change to configurable when Lambda Extensions API supports getting environment variable by primitives in next week.
```yaml
extensions:
  health_check:
  pprof:
    endpoint: 0.0.0.0:1777
  zpages:
    endpoint: 0.0.0.0:55679

receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:55680

processors:
  batch:
  queued_retry:

exporters:
  logging:
    loglevel: debug
  awsxray:
    local_mode: true
    region: 'us-west-2'

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [logging, awsxray]
    metrics:
      receivers: [otlp]
      exporters: [logging]
  extensions: [health_check, pprof, zpages]
```

By default OTel auto instrumentation uses SpanBatchProcessor, batching timer is 5 seconds. You will see X-Ray segments delay caused by Lambda freeze.
Changing otel.bsp.schedule.delay to 0 can mitigate the delay.
