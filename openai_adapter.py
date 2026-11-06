"""Small opt-in adapter for completed OpenAI Responses API objects."""
MAX_SAFE_TOKENS=9_007_199_254_740_991

def _value(obj,name):
    return obj.get(name) if isinstance(obj,dict) else getattr(obj,name,None)

def response_tokens(response):
    """Return input + output tokens from a completed response, or zero if absent."""
    usage=_value(response,'usage')
    if usage is None:return 0
    values=(_value(usage,'input_tokens'),_value(usage,'output_tokens'))
    if any(type(value) is not int or not 0<=value<=MAX_SAFE_TOKENS for value in values):
        raise ValueError('OpenAI response usage must contain JSON-safe non-negative input_tokens and output_tokens')
    total=sum(values)
    if total>MAX_SAFE_TOKENS:raise ValueError('OpenAI response token total exceeds the JSON-safe integer range')
    return total

def record_response_call(recorder, create, *args, tool='openai.responses.create', **kwargs):
    """Call a synchronous Responses-compatible callable without recording inputs or output."""
    with recorder.span(tool) as span_id:
        response=create(*args,**kwargs)
    recorder.set_tokens(span_id,response_tokens(response))
    return response
