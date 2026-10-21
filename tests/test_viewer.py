import unittest
from app import summarize
from viewer import render_viewer

class ViewerTests(unittest.TestCase):
    def test_renders_accessible_timeline_and_escapes_trace_fields(self):
        trace={'version':1,'spans':[{'id':'root<script>','tool':'agent & plan','duration_ms':100,'start_ms':0,'status':'ok','tokens':3},{'id':'bad','tool':'shell','duration_ms':20,'start_ms':20,'status':'error'}]}
        html=render_viewer(trace,summarize(trace))
        self.assertIn('Failures only',html);self.assertIn('data-status="error"',html);self.assertIn('agent &amp; plan',html);self.assertNotIn('root<script>',html)
        self.assertIn('2</b><span>SPANS',html);self.assertIn('3</b><span>REPORTED TOKENS',html)
