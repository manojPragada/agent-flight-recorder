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


    def test_parent_hierarchy_and_overlap_timing(self):
        t={'version':1,'spans':[{'id':'root','tool':'agent','duration_ms':100,'start_ms':0,'status':'ok'},{'id':'child','parent_id':'root','tool':'model','duration_ms':40,'start_ms':20,'status':'ok'}]}
        result=summarize(t)
        self.assertEqual(result['root_span_ids'],['root']);self.assertEqual(result['max_depth'],2)
        self.assertEqual(result['timing'],{'elapsed_ms':100,'busy_ms':100})
        self.assertEqual(result['summed_duration_ms'],140)
    def test_disjoint_intervals_exclude_idle_gaps(self):
        t={'version':1,'spans':[{'id':'a','tool':'x','duration_ms':10,'start_ms':5,'status':'ok'},{'id':'b','tool':'x','duration_ms':10,'start_ms':25,'status':'ok'}]}
        self.assertEqual(summarize(t)['timing'],{'elapsed_ms':30,'busy_ms':20})
    def test_missing_parent_and_cycles(self):
        for parent in ['missing','a',[]]:
            t=self.trace();t['spans'][0]['parent_id']=parent
            with self.assertRaises(ValueError):summarize(t)
        t={'version':1,'spans':[{'id':'a','parent_id':'b','tool':'x','duration_ms':1,'status':'ok'},{'id':'b','parent_id':'a','tool':'x','duration_ms':1,'status':'ok'}]}
        with self.assertRaises(ValueError):summarize(t)
    def test_partial_and_invalid_timestamps(self):
        for value in [-1,True,float('nan')]:
            t=self.trace();t['spans'][0]['start_ms']=value
            with self.assertRaises(ValueError):summarize(t)
        t=self.trace();t['spans'][0]['start_ms']=0;t['spans'].append({'id':'b','tool':'x','duration_ms':1,'status':'ok'})
        with self.assertRaises(ValueError):summarize(t)
    def test_child_must_fit_parent_interval(self):
        t={'version':1,'spans':[{'id':'a','tool':'x','duration_ms':10,'start_ms':0,'status':'ok'},{'id':'b','parent_id':'a','tool':'x','duration_ms':20,'start_ms':0,'status':'ok'}]}
        with self.assertRaises(ValueError):summarize(t)

    def test_invalid_parent_timestamp_is_order_independent(self):
        t={'version':1,'spans':[{'id':'child','parent_id':'parent','tool':'x','duration_ms':1,'start_ms':0,'status':'ok'},{'id':'parent','tool':'x','duration_ms':10,'start_ms':'invalid','status':'ok'}]}
        with self.assertRaises(ValueError):summarize(t)


    def test_longest_dependency_chain(self):
        t={'version':1,'spans':[{'id':name,'tool':'x','duration_ms':duration,'status':'ok','depends_on':deps} for name,duration,deps in [('a',10,[]),('b',20,['a']),('c',5,['a']),('d',10,['b','c'])]]}
        self.assertEqual(summarize(t)['critical_path'],{'duration_ms':40,'span_ids':['a','b','d']})
    def test_dependency_analysis_excludes_inclusive_parent_duration(self):
        t={'version':1,'spans':[{'id':'root','tool':'agent','duration_ms':100,'status':'ok'},{'id':'a','parent_id':'root','tool':'model','duration_ms':10,'status':'ok','depends_on':[]}]}
        self.assertEqual(summarize(t)['critical_path'],{'duration_ms':10,'span_ids':['a']})
    def test_dependency_missing_cycle_and_duplicate_rejected(self):
        for dependencies in [['missing'],['a'],['a','a'],'a',None]:
            t=self.trace();t['spans'][0]['depends_on']=dependencies
            with self.assertRaises(ValueError):summarize(t)
    def test_dependency_must_finish_before_successor(self):
        t={'version':1,'spans':[{'id':'a','tool':'x','duration_ms':10,'start_ms':0,'status':'ok','depends_on':[]},{'id':'b','tool':'x','duration_ms':10,'start_ms':5,'status':'ok','depends_on':['a']}]}
        with self.assertRaises(ValueError):summarize(t)
    def test_no_dependencies_does_not_invent_critical_path(self):
        self.assertIsNone(summarize(self.trace())['critical_path'])

