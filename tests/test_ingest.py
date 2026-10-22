import io
import unittest
from ingest import read_ndjson
from app import summarize

class IngestTests(unittest.TestCase):
    def test_reads_blank_separated_span_events(self):
        source='{"id":"a","tool":"model","duration_ms":4,"status":"ok"}\n\n{"id":"b","tool":"search","duration_ms":2,"status":"error"}\n'
        trace=read_ndjson(io.StringIO(source));self.assertEqual(summarize(trace)['span_count'],2);self.assertEqual(trace['spans'][1]['id'],'b')
    def test_reports_line_for_malformed_events(self):
        for source,message in [('[]\n','Line 1 must'),('{broken}\n','Line 1 is not')]:
            with self.assertRaisesRegex(ValueError,message):read_ndjson(io.StringIO(source))
    def test_bounds_event_count_and_line_size(self):
        with self.assertRaisesRegex(ValueError,'exceeds 1 spans'):read_ndjson(io.StringIO('{}\n{}\n'),max_spans=1)
        with self.assertRaisesRegex(ValueError,'256 KiB'):read_ndjson(io.StringIO('12345\n'),max_line_bytes=4)
