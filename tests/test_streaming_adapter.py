import unittest
from streaming_adapter import completed_stream_tokens,record_completed_stream,record_openai_response_stream
from instrumentation import TraceRecorder
class Recorder:
 def __init__(self):self.tokens=[]
 class Span:
  def __enter__(self):return 'span'
  def __exit__(self,*args):pass
 def span(self,tool):return self.Span()
 def set_tokens(self,span,value):self.tokens.append((span,value))
class StreamingTests(unittest.TestCase):
 def test_usage_is_committed_only_from_completed_event(self):
  recorder=Recorder();events=[{'type':'delta','usage':{'input_tokens':99,'output_tokens':99}},{'type':'response.completed','usage':{'input_tokens':3,'output_tokens':4}}]
  self.assertEqual(list(record_completed_stream(recorder,events)),events);self.assertEqual(recorder.tokens,[('span',7)])
 def test_partial_stream_has_no_usage_claim(self):
  recorder=Recorder();list(record_completed_stream(recorder,[{'type':'delta'}]));self.assertEqual(recorder.tokens,[])
 def test_multiple_completion_events_are_rejected(self):
  event={'type':'response.completed','usage':{'input_tokens':1,'output_tokens':1}}
  with self.assertRaisesRegex(ValueError,'multiple'):list(record_completed_stream(Recorder(),[event,event]))
 def test_generic_completion_must_be_terminal(self):
  event={'type':'message_stop','usage':{'input_tokens':1,'output_tokens':1}}
  with self.assertRaisesRegex(ValueError,'after completion'):list(record_completed_stream(Recorder(),[event,{'type':'delta'}]))
 def test_openai_completed_event_reads_nested_response_usage(self):
  recorder=Recorder();events=[{'type':'response.output_text.delta','delta':'secret'},{'type':'response.completed','response':{'usage':{'input_tokens':2,'output_tokens':5},'output':'not retained'}}]
  self.assertEqual(list(record_openai_response_stream(recorder,events)),events);self.assertEqual(recorder.tokens,[('span',7)])
 def test_openai_partial_stream_makes_no_usage_claim(self):
  recorder=Recorder();list(record_openai_response_stream(recorder,[{'type':'response.output_text.delta','delta':'secret'}]));self.assertEqual(recorder.tokens,[])
 def test_real_recorder_commits_after_span_completion(self):
  recorder=TraceRecorder();list(record_openai_response_stream(recorder,[{'type':'response.completed','response':{'usage':{'input_tokens':1,'output_tokens':2}}}]));self.assertEqual(recorder.spans[0]['tokens'],3)
 def test_openai_completion_must_be_terminal(self):
  event={'type':'response.completed','response':{'usage':{'input_tokens':1,'output_tokens':2}}}
  with self.assertRaisesRegex(ValueError,'after response.completed'):list(record_openai_response_stream(Recorder(),[event,{'type':'response.output_text.delta'}]))
