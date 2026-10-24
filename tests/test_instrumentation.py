import unittest
from instrumentation import TraceRecorder
from app import summarize

class Clock:
    def __init__(self):self.value=10
    def __call__(self):self.value+=.01;return self.value

class InstrumentationTests(unittest.TestCase):
    def test_nested_contexts_emit_valid_parented_trace(self):
        recorder=TraceRecorder(Clock())
        with recorder.span('agent',span_id='root',tokens=2):
            with recorder.span('search',span_id='child'):pass
        trace=recorder.trace();summary=summarize(trace)
        self.assertEqual(summary['span_count'],2);self.assertEqual(summary['failures'],0)
        child=next(span for span in trace['spans'] if span['id']=='child');self.assertEqual(child['parent_id'],'root')
    def test_failures_are_recorded_without_capturing_arguments(self):
        recorder=TraceRecorder(Clock())
        @recorder.instrument('danger')
        def fail(secret):raise RuntimeError('boom')
        with self.assertRaises(RuntimeError):fail('do-not-record')
        self.assertEqual(recorder.spans[0]['status'],'error');self.assertNotIn('do-not-record',repr(recorder.trace()))
    def test_invalid_metadata_rejected(self):
        recorder=TraceRecorder(Clock())
        with self.assertRaises(ValueError):
            with recorder.span('',span_id='x'):pass
        with self.assertRaises(ValueError):
            with recorder.span('tool',tokens=-1):pass
