import unittest
from app import summarize
class Tests(unittest.TestCase):
    def trace(self):return {'version':1,'spans':[{'id':'a','tool':'model','duration_ms':100,'tokens':8,'status':'error'}]}
    def test_summary(self):
        s=summarize(self.trace());self.assertEqual((s['failures'],s['tokens'],s['summed_duration_ms']),(1,8,100))
    def test_duplicates(self):
        t=self.trace();t['spans']*=2
        with self.assertRaises(ValueError):summarize(t)
    def test_invalid_numbers(self):
        for value in [-1,True,float('nan'),float('inf')]:
            t=self.trace();t['spans'][0]['duration_ms']=value
            with self.assertRaises(ValueError):summarize(t)
    def test_empty(self):self.assertEqual(summarize({'version':1,'spans':[]})['span_count'],0)
