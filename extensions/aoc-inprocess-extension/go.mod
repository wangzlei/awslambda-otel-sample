module aws-lambda-extensions/aoc-extension

go 1.14

require (
	github.com/open-telemetry/opentelemetry-collector-contrib/exporter/awsemfexporter v0.14.1-0.20201117192543-4a81c809e720
	github.com/open-telemetry/opentelemetry-collector-contrib/exporter/awsxrayexporter v0.14.1-0.20201111210848-994cabe5d596
	github.com/open-telemetry/opentelemetry-collector-contrib/processor/metricstransformprocessor v0.14.1-0.20201111210848-994cabe5d596
	github.com/open-telemetry/opentelemetry-collector-contrib/receiver/awsecscontainermetricsreceiver v0.14.1-0.20201111210848-994cabe5d596
	github.com/open-telemetry/opentelemetry-collector-contrib/receiver/awsxrayreceiver v0.14.1-0.20201111210848-994cabe5d596
	go.opentelemetry.io/collector v0.14.1-0.20201112191733-c6d9a2be2223
	github.com/spf13/viper v1.7.1
	go.uber.org/zap v1.16.0
)

replace github.com/open-telemetry/opentelemetry-collector-contrib/internal/awsxray => github.com/open-telemetry/opentelemetry-collector-contrib/internal/awsxray v0.14.1-0.20201111210848-994cabe5d596