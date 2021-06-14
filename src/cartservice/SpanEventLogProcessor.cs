using System.Diagnostics;
using OpenTelemetry;
using OpenTelemetry.Logs;
using OpenTelemetry.Trace;

namespace cartservice.OpenTelemetry
{
    internal class SpanEventLogProcessor : BaseProcessor<LogRecord>
    {
        private readonly string name;

        public SpanEventLogProcessor(string name = "SpanEventLogProcessor")
        {
            this.name = name;
        }

        public override void OnEnd(LogRecord data)
        {
            if (Activity.Current == null) return;

            var tags = new ActivityTagsCollection
            {
                { nameof(data.CategoryName), data.CategoryName },
                { nameof(data.LogLevel), data.LogLevel },
                { nameof(data.State), data.State.ToString() }
            };

            var activityEvent = new ActivityEvent("log", data.Timestamp, tags);
            Activity.Current.AddEvent(activityEvent);

            // if (data.Exception != null)
            // {
            //     Activity.Current.RecordException(data.Exception);
            // }
        }
    }
}