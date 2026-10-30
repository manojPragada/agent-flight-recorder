"""Provider-neutral completion-gated token accounting for streaming adapters."""
def _value(value,name):return value.get(name) if isinstance(value,dict) else getattr(value,name,None)
def completed_stream_tokens(event):
    """Return tokens only for an explicitly completed final event."""
    if _value(event,'type') not in {'response.completed','message_stop'}:return None
    usage=_value(event,'usage')
    if usage is None:return None
    values=(_value(usage,'input_tokens'),_value(usage,'output_tokens'))
    if any(type(value) is not int or value<0 for value in values):raise ValueError('Completed stream usage must contain non-negative input_tokens and output_tokens')
    return sum(values)
def openai_completed_event_tokens(event):
    """Read usage only from the response object on a Responses API completed event."""
    if _value(event,'type')!='response.completed':return None
    response=_value(event,'response')
    if response is None:raise ValueError('OpenAI response.completed event requires a response object')
    usage=_value(response,'usage')
    if usage is None:raise ValueError('Completed OpenAI response requires usage')
    values=(_value(usage,'input_tokens'),_value(usage,'output_tokens'))
    if any(type(value) is not int or value<0 for value in values):raise ValueError('Completed OpenAI response usage must contain non-negative input_tokens and output_tokens')
    return sum(values)
def record_openai_response_stream(recorder,events,*,tool='openai.responses.stream'):
    """Yield Responses API events unchanged and commit only final response usage."""
    completed=False;final_tokens=None
    with recorder.span(tool) as span_id:
        for event in events:
            tokens=openai_completed_event_tokens(event)
            if completed:
                if tokens is not None:raise ValueError('Stream contains multiple response.completed events')
                raise ValueError('Stream contains an event after response.completed')
            if tokens is not None:
                if completed:raise ValueError('Stream contains multiple response.completed events')
                completed=True;final_tokens=tokens
            yield event
    if final_tokens is not None:recorder.set_tokens(span_id,final_tokens)
def record_completed_stream(recorder,events,*,tool='provider.stream'):
    """Yield events unchanged and commit usage only after normal completion."""
    completed=False;final_tokens=None
    with recorder.span(tool) as span_id:
        for event in events:
            tokens=completed_stream_tokens(event)
            if completed:
                if tokens is not None:raise ValueError('Stream contains multiple completed usage events')
                raise ValueError('Stream contains an event after completion')
            if tokens is not None:
                if completed:raise ValueError('Stream contains multiple completed usage events')
                completed=True;final_tokens=tokens
            yield event
    if final_tokens is not None:recorder.set_tokens(span_id,final_tokens)
