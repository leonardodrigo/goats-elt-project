import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource


# otel_setup.py
def setup_otel_logging(
    otel_collector_host: str,
    otel_collector_port: int,
    level=logging.DEBUG,
):
    logger_provider = LoggerProvider(
        resource=Resource.create(
            {
                "service.name": "goats-elt",
                "service.instance.id": "goats-elt-instance",
            }
        ),
    )
    set_logger_provider(logger_provider)

    # Configure OTLP exporter to send logs to the collector
    exporter = OTLPLogExporter(
        endpoint=f"http://{otel_collector_host}:{otel_collector_port}/v1/logs"
    )

    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
