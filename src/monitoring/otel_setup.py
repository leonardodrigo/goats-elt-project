import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.resources import Resource

# otel_setup.py
def setup_otel_logging(level=logging.DEBUG):
    logger_provider = LoggerProvider(
        resource=Resource.create({
            "service.name": "goats-elt",
            "service.instance.id": "goats-elt-instance",
        }),
    )
    set_logger_provider(logger_provider)
    
    exporter = ConsoleLogExporter()
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
