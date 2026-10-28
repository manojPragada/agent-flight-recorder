import unittest
from streaming_adapter import completed_stream_tokens,record_completed_stream
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
