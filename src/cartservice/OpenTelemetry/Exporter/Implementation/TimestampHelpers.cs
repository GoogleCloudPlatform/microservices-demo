// <copyright file="TimestampHelpers.cs" company="OpenTelemetry Authors">
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

using System;

namespace OpenTelemetry.Exporter.OpenTelemetryProtocol.Implementation
{
    /// <summary>
    /// Helpers to convert .NET time related types to the timestamp used in OTLP.
    /// </summary>
    internal static class TimestampHelpers
    {
        private const long NanosecondsPerTicks = 100;
        private const long UnixEpochTicks = 621355968000000000; // = DateTimeOffset.FromUnixTimeMilliseconds(0).Ticks

        internal static long ToUnixTimeNanoseconds(this DateTime dt)
        {
            return (dt.Ticks - UnixEpochTicks) * NanosecondsPerTicks;
        }

        internal static long ToUnixTimeNanoseconds(this DateTimeOffset dto)
        {
            return (dto.Ticks - UnixEpochTicks) * NanosecondsPerTicks;
        }

        internal static long ToNanoseconds(this TimeSpan duration)
        {
            return duration.Ticks * NanosecondsPerTicks;
        }
    }
}
