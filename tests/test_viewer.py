import unittest
from app import summarize
from viewer import render_viewer

class ViewerTests(unittest.TestCase):
    def test_renders_accessible_timeline_and_escapes_trace_fields(self):
        trace={'version':1,'spans':[{'id':'root<script>','tool':'agent & plan','duration_ms':100,'start_ms':0,'status':'ok','tokens':3},{'id':'bad','tool':'shell','duration_ms':20,'start_ms':20,'status':'error','error_type':'tool.timeout'}]}
        html=render_viewer(trace,summarize(trace))
        self.assertIn('Failures only',html);self.assertIn('data-status="error"',html);self.assertIn('agent &amp; plan',html);self.assertNotIn('root<script>',html)
        self.assertIn('2</b><span>SPANS',html);self.assertIn('3</b><span>REPORTED TOKENS',html);self.assertIn('tool.timeout',html)
        self.assertIn('<option value="tool.timeout">tool.timeout</option>',html)
        self.assertIn('data-failure="tool.timeout"',html)
        self.assertIn('filter-status',html);self.assertIn('spans visible',html);self.assertIn('aria-live',html)
        self.assertIn('data-duration="100"',html);self.assertIn('summed ms.',html)

    def test_failure_filter_contains_only_classifications(self):
        trace={'version':1,'spans':[{'id':'bad','tool':'shell','duration_ms':20,'status':'error','error_type':'tool.timeout'}]}
        html=render_viewer(trace,summarize(trace))
        self.assertIn('Failure type',html)
        self.assertNotIn('secret exception detail',html)
        self.assertIn('No spans match these filters.',html)
