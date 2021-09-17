// <copyright file="LogRecordExtensions.cs" company="OpenTelemetry Authors">
// Copyright The OpenTelemetry Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// </copyright>

// #if NETSTANDARD2_0 || NETSTANDARD2_1
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using Google.Protobuf;
using Google.Protobuf.Collections;
using OpenTelemetry;
using OpenTelemetry.Internal;
using OpenTelemetry.Logs;
using OtlpCollector = Opentelemetry.Proto.Collector.Logs.V1;
using OtlpCommon = Opentelemetry.Proto.Common.V1;
using OtlpLogs = Opentelemetry.Proto.Logs.V1;
using OtlpResource = Opentelemetry.Proto.Resource.V1;

namespace OpenTelemetry.Exporter.OpenTelemetryProtocol.Implementation
{
    internal static class LogRecordExtensions
    {
        private static readonly ConcurrentBag<OtlpLogs.InstrumentationLibraryLogs> SpanListPool = new ConcurrentBag<OtlpLogs.InstrumentationLibraryLogs>();
        private static readonly Action<RepeatedField<OtlpLogs.LogRecord>, int> RepeatedFieldOfSpanSetCountAction = CreateRepeatedFieldOfSpanSetCountAction();

        internal static void AddBatch(
            this OtlpCollector.ExportLogsServiceRequest request,
            OtlpResource.Resource processResource,
            in Batch<LogRecord> activityBatch)
        {
            Dictionary<string, OtlpLogs.InstrumentationLibraryLogs> logRecordsByLibrary = new Dictionary<string, OtlpLogs.InstrumentationLibraryLogs>();
            OtlpLogs.ResourceLogs resourceSpans = new OtlpLogs.ResourceLogs
            {
                Resource = processResource,
            };
            request.ResourceLogs.Add(resourceSpans);

            foreach (var activity in activityBatch)
            {
                OtlpLogs.LogRecord span = activity.ToOtlpLog();
                if (span == null)
                {
                    OpenTelemetryProtocolExporterEventSource.Log.CouldNotTranslateActivity(
                        nameof(ActivityExtensions),
                        nameof(AddBatch));
                    continue;
                }

                // TODO: Source/Version
                var logRecordSourceName = "OpenTelemetry Logs";
                if (!logRecordsByLibrary.TryGetValue(logRecordSourceName, out var logRecords))
                {
                    logRecords = GetSpanListFromPool(logRecordSourceName, "1.2.3");

                    logRecordsByLibrary.Add(logRecordSourceName, logRecords);
                    resourceSpans.InstrumentationLibraryLogs.Add(logRecords);
                }

                logRecords.Logs.Add(span);
            }
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        internal static void Return(this OtlpCollector.ExportLogsServiceRequest request)
        {
            var resourceSpans = request.ResourceLogs.FirstOrDefault();
            if (resourceSpans == null)
            {
                return;
            }

            foreach (var librarySpans in resourceSpans.InstrumentationLibraryLogs)
            {
                RepeatedFieldOfSpanSetCountAction(librarySpans.Logs, 0);
                SpanListPool.Add(librarySpans);
            }
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        internal static OtlpLogs.InstrumentationLibraryLogs GetSpanListFromPool(string name, string version)
        {
            if (!SpanListPool.TryTake(out var spans))
            {
                spans = new OtlpLogs.InstrumentationLibraryLogs
                {
                    InstrumentationLibrary = new OtlpCommon.InstrumentationLibrary
                    {
                        Name = name, // Name is enforced to not be null, but it can be empty.
                        Version = version ?? string.Empty, // NRE throw by proto
                    },
                };
            }
            else
            {
                spans.InstrumentationLibrary.Name = name;
                spans.InstrumentationLibrary.Version = version ?? string.Empty;
            }

            return spans;
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        internal static OtlpLogs.LogRecord ToOtlpLog(this LogRecord logRecord)
        {
            byte[] traceIdBytes = new byte[16];
            byte[] spanIdBytes = new byte[8];

            logRecord.TraceId.CopyTo(traceIdBytes);
            logRecord.SpanId.CopyTo(spanIdBytes);

            var otlpLogRecord = new OtlpLogs.LogRecord
            {
                Name = logRecord.CategoryName,
                Body = new OtlpCommon.AnyValue { StringValue = logRecord.State.ToString() },
                SeverityText = logRecord.LogLevel.ToString(),

                // TODO: convert LogLevel to OTel severity
                // SeverityNumber = activity.LogLevel,
                TimeUnixNano = (ulong)logRecord.Timestamp.ToUnixTimeNanoseconds(),
                TraceId = UnsafeByteOperations.UnsafeWrap(traceIdBytes),
                SpanId = UnsafeByteOperations.UnsafeWrap(spanIdBytes),
            };

            // TODO: Add attributes

            // Activity does not limit number of attributes, events, links, etc so drop counts are always zero.

            return otlpLogRecord;
        }

        private static Action<RepeatedField<OtlpLogs.LogRecord>, int> CreateRepeatedFieldOfSpanSetCountAction()
        {
            FieldInfo repeatedFieldOfSpanCountField = typeof(RepeatedField<OtlpLogs.LogRecord>).GetField("count", BindingFlags.NonPublic | BindingFlags.Instance);

            DynamicMethod dynamicMethod = new DynamicMethod(
                "CreateSetCountAction",
                null,
                new[] { typeof(RepeatedField<OtlpLogs.LogRecord>), typeof(int) },
                typeof(LogRecordExtensions).Module,
                skipVisibility: true);

            var generator = dynamicMethod.GetILGenerator();

            generator.Emit(OpCodes.Ldarg_0);
            generator.Emit(OpCodes.Ldarg_1);
            generator.Emit(OpCodes.Stfld, repeatedFieldOfSpanCountField);
            generator.Emit(OpCodes.Ret);

            return (Action<RepeatedField<OtlpLogs.LogRecord>, int>)dynamicMethod.CreateDelegate(typeof(Action<RepeatedField<OtlpLogs.LogRecord>, int>));
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        private static OtlpCommon.KeyValue CreateOtlpKeyValue(string key, OtlpCommon.AnyValue value)
        {
            return new OtlpCommon.KeyValue { Key = key, Value = value };
        }
    }
}
// #endif
