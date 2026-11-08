import unittest
from instrumentation import TraceRecorder
from app import summarize
from openai_adapter import record_response_call,response_tokens
from anthropic_adapter import record_message_call,message_tokens

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
        for tool,span_id in [('bad\ntool','x'),('tool','bad\x7fid')]:
            with self.assertRaisesRegex(ValueError,'control-free'):
                with recorder.span(tool,span_id=span_id):pass
    def test_openai_adapter_records_only_timing_and_reported_tokens(self):
        recorder=TraceRecorder(Clock());secret='do-not-record'
        response=record_response_call(recorder,lambda **kwargs:{'usage':{'input_tokens':7,'output_tokens':3},'output_text':secret},input=secret)
        self.assertEqual(response['output_text'],secret);self.assertEqual(recorder.spans[0]['tokens'],10)
        self.assertNotIn(secret,repr(recorder.trace()))
    def test_openai_usage_must_be_complete_and_non_negative(self):
        self.assertEqual(response_tokens({}),0)
        with self.assertRaises(ValueError):response_tokens({'usage':{'input_tokens':1,'output_tokens':None}})
    def test_anthropic_adapter_includes_cache_usage_without_content(self):
        recorder=TraceRecorder(Clock());secret='private prompt'
        message=record_message_call(recorder,lambda **kwargs:{'usage':{'input_tokens':4,'cache_creation_input_tokens':2,'cache_read_input_tokens':3,'output_tokens':1},'content':secret},messages=[secret])
        self.assertEqual(message['content'],secret);self.assertEqual(recorder.spans[0]['tokens'],10);self.assertNotIn(secret,repr(recorder.trace()))
    def test_anthropic_usage_rejects_invalid_counts(self):
        self.assertEqual(message_tokens({}),0)
        with self.assertRaises(ValueError):message_tokens({'usage':{'input_tokens':-1,'output_tokens':2}})
    def test_synchronous_usage_stays_json_safe(self):
        maximum=9_007_199_254_740_991
        with self.assertRaisesRegex(ValueError,'JSON-safe'):response_tokens({'usage':{'input_tokens':maximum,'output_tokens':1}})
        with self.assertRaisesRegex(ValueError,'JSON-safe'):message_tokens({'usage':{'input_tokens':maximum,'output_tokens':1}})
        recorder=TraceRecorder(Clock())
        with self.assertRaisesRegex(ValueError,'JSON-safe'):
            with recorder.span('tool',tokens=maximum+1):pass
