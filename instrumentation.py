"""Dependency-free instrumentation that emits provider-neutral span dictionaries."""
import contextlib
import time
import uuid
MAX_SAFE_TOKENS=9_007_199_254_740_991

def _label(value,name):
    if not isinstance(value,str) or not value or len(value)>200 or any(ord(character)<32 or ord(character)==127 for character in value):raise ValueError(f'{name} must be a control-free 1–200 character string')
    return value

def _tokens(value):
    if type(value) is not int or not 0<=value<=MAX_SAFE_TOKENS:raise ValueError('tokens must be a JSON-safe non-negative integer')
    return value

class TraceRecorder:
    def __init__(self, clock=time.perf_counter):
        self.clock=clock;self.origin=clock();self.spans=[];self._stack=[]

    @contextlib.contextmanager
    def span(self, tool, *, span_id=None, tokens=0):
        _label(tool,'tool')
        _tokens(tokens)
        identifier=span_id or uuid.uuid4().hex
        _label(identifier,'span_id')
        if any(s['id']==identifier for s in self.spans):raise ValueError('span_id must be unique')
        start=self.clock();parent=self._stack[-1] if self._stack else None;self._stack.append(identifier);status='ok'
        try:yield identifier
        except BaseException:
            status='error';raise
        finally:
            end=self.clock();self._stack.pop()
            self.spans.append({'id':identifier,'tool':tool,'duration_ms':max(0,(end-start)*1000),'status':status,'tokens':tokens,'parent_id':parent,'start_ms':max(0,(start-self.origin)*1000)})

    def trace(self):
        return {'version':1,'spans':list(self.spans)}

    def set_tokens(self, span_id, tokens):
        _tokens(tokens)
        for span in reversed(self.spans):
            if span['id']==span_id:span['tokens']=tokens;return
        raise ValueError('span_id has not completed')

    def instrument(self, tool, *, tokens=0):
        def decorate(function):
            def wrapped(*args,**kwargs):
                with self.span(tool,tokens=tokens):return function(*args,**kwargs)
            wrapped.__name__=getattr(function,'__name__','instrumented')
            wrapped.__doc__=getattr(function,'__doc__',None)
            return wrapped
        return decorate
