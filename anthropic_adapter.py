"""Opt-in adapter for completed Anthropic Messages API objects."""

def _value(obj,name,default=None):
    return obj.get(name,default) if isinstance(obj,dict) else getattr(obj,name,default)

def message_tokens(message):
    usage=_value(message,'usage')
    if usage is None:return 0
    names=('input_tokens','cache_creation_input_tokens','cache_read_input_tokens','output_tokens')
    values=[_value(usage,name,0) for name in names]
    if any(type(value) is not int or value<0 for value in values):raise ValueError('Anthropic message usage token counts must be non-negative integers')
    return sum(values)

def record_message_call(recorder, create, *args, tool='anthropic.messages.create', **kwargs):
    """Call a synchronous Messages-compatible callable without recording content."""
    with recorder.span(tool) as span_id:message=create(*args,**kwargs)
    recorder.set_tokens(span_id,message_tokens(message));return message
