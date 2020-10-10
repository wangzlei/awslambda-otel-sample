import logging
import opentelemetry.trace as trace_api
import json
from opentelemetry.sdk.trace.export import Span, SpanExporter, SpanExportResult
from opentelemetry.trace import SpanKind
from .emitter import UDPEmitter
import time
import binascii
import os
import random
import datetime

logger = logging.getLogger(__name__)

class XrayDaemonSpanExporter(SpanExporter):
    TRACE_ID_VERSION = "1"
    TRACE_ID_DELIMITER = "-"
    TRACE_ID_FIRST_PART_LENGTH = 8

    def __init__(self):
        self._emitter = UDPEmitter()


    def export(self, spans) -> SpanExportResult:
        logger.info('-----------------XrayDaemonSpanExporter emit ----------')
        for span in spans:
            segment = self._translate_to_segment(span)
            entity = json.dumps(segment)
            self._emitter.send_entity(entity)

        return SpanExportResult.SUCCESS 

    def shutdown(self) -> None:
        pass

    def _translate_to_segment(self, span):
        segment = {}
        segment['name'] = span.name
        
        # traceid, id, parent
        otel_trace_id = "{:032x}".format(span.context.trace_id)
        xray_trace_id = (
            self.TRACE_ID_VERSION +
            self.TRACE_ID_DELIMITER +
            otel_trace_id[:self.TRACE_ID_FIRST_PART_LENGTH] +
            self.TRACE_ID_DELIMITER +
            otel_trace_id[self.TRACE_ID_FIRST_PART_LENGTH:]
        )
        id = "{:016x}".format(span.context.span_id)
        segment['trace_id'] = xray_trace_id
        segment['id'] = id

        parent_context = span.parent
        if parent_context:
            parent_id = "{:016x}".format(parent_context.span_id)
            segment['parent_id'] = parent_id
            segment['type'] = 'subsegment'
            # TODO: aws or remote
            segment['namespace'] = 'aws'
        else:
            segment['type'] = 'segment'

        if 'aws.origin' in span.attributes._dict:
            segment['origin'] = 'AWS::Lambda::Function'
        
        # no idea what is the best practice Python process time
        segment['start_time'] = span._start_time/1000000000
        segment['end_time'] = span._end_time/1000000000

        # xray resources
        segment['aws'] = span.resource._attributes

        # throw everything into metadata
        awsDict = {**(span.attributes._dict), **(span.resource._attributes)}
        segment['metadata'] = awsDict

        return segment
