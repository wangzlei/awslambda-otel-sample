import logging
import opentelemetry.trace as trace_api
from opentelemetry.sdk.trace.export import Span, SpanExporter, SpanExportResult
from .emitter import UDPEmitter

logger = logging.getLogger(__name__)

class XrayDaemonSpanExporter(SpanExporter):
    def __init__(self):
        self._emitter = UDPEmitter()


    def export(self, spans) -> SpanExportResult:
        self._emitter.send_entity('')
        logger.info('-----------------XrayDaemonSpanExporter emit ----------')
        return SpanExportResult.SUCCESS 

    def shutdown(self) -> None:
        pass