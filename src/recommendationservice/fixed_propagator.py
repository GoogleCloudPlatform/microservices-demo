import typing

import opentelemetry.trace as trace
from opentelemetry.context import Context
from opentelemetry.sdk.trace.propagation.b3_format import (
    B3Format,
    format_trace_id,
    format_span_id,
)
from opentelemetry.trace.propagation.textmap import (
    Setter,
    TextMapPropagatorT,
)

class FixedB3Format(B3Format):

    def inject(
        self,
        set_in_carrier: Setter[TextMapPropagatorT],
        carrier: TextMapPropagatorT,
        context: typing.Optional[Context] = None,
    ) -> None:
        span = trace.get_current_span(context=context)

        span_context = span.get_context()
        if span_context == trace.INVALID_SPAN_CONTEXT:
            return

        sampled = (trace.TraceFlags.SAMPLED & span_context.trace_flags) != 0
        set_in_carrier(
            carrier, self.TRACE_ID_KEY, format_trace_id(span_context.trace_id),
        )
        set_in_carrier(
            carrier, self.SPAN_ID_KEY, format_span_id(span_context.span_id)
        )
        if getattr(span, 'parent', None) is not None:
            set_in_carrier(
                carrier,
                self.PARENT_SPAN_ID_KEY,
                format_span_id(span.parent.span_id),
            )
        set_in_carrier(carrier, self.SAMPLED_KEY, "1" if sampled else "0")
