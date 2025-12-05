import logging

from opentelemetry import metrics
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes


def setup_otel(
    otel_collector_host: str,
    otel_collector_port: int,
    log_level=logging.DEBUG,
):
    """Set up OpenTelemetry logging and optionally metrics."""

    # Shared resource for both signals
    resource = Resource.create(
        {
            ResourceAttributes.SERVICE_NAME: "goats-elt",
            ResourceAttributes.SERVICE_INSTANCE_ID: "goats-elt-instance",
            ResourceAttributes.SERVICE_VERSION: "0.1.0",
        }
    )

    base_endpoint = f"http://{otel_collector_host}:{otel_collector_port}"

    # Logging setup
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)

    log_exporter = OTLPLogExporter(endpoint=f"{base_endpoint}/v1/logs")
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # Metrics setup
    meter_provider = None
    metric_exporter = OTLPMetricExporter(endpoint=f"{base_endpoint}/v1/metrics")
    reader = PeriodicExportingMetricReader(
        exporter=metric_exporter,
        export_interval_millis=3000,
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)

    return logger_provider, meter_provider
