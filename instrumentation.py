"""Dependency-free instrumentation that emits provider-neutral span dictionaries."""
import contextlib
import time
import uuid

class TraceRecorder:
    def __init__(self, clock=time.perf_counter):
        self.clock=clock;self.origin=clock();self.spans=[];self._stack=[]

    @contextlib.contextmanager
    def span(self, tool, *, span_id=None, tokens=0):
        if not isinstance(tool,str) or not tool or len(tool)>200:raise ValueError('tool must be 1–200 characters')
        if type(tokens) is not int or tokens<0:raise ValueError('tokens must be a non-negative integer')
        identifier=span_id or uuid.uuid4().hex
        if not isinstance(identifier,str) or not identifier or len(identifier)>200 or any(s['id']==identifier for s in self.spans):
            raise ValueError('span_id must be a unique 1–200 character string')
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
        if type(tokens) is not int or tokens<0:raise ValueError('tokens must be a non-negative integer')
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
