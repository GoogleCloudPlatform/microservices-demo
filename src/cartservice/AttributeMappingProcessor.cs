// Copyright 2020 Splunk LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using OpenTelemetry;
using OpenTelemetry.Trace;

internal class AttrMappingProcessor : ActivityProcessor
{

  private static double REDIS_SPAN_ERROR_RATE = Convert.ToDouble(Environment.GetEnvironmentVariable("REDIS_SPAN_ERROR_RATE"));
  private static string EXTERNAL_DB_NAME = Environment.GetEnvironmentVariable("EXTERNAL_DB_NAME") ?? "global.datastore";
  private static double EXTERNAL_DB_CHANGE_RATE = Convert.ToDouble(Environment.GetEnvironmentVariable("EXTERNAL_DB_CHANGE_RATE"));


  public Random _random;


  public AttrMappingProcessor()
  {
    _random = new Random();
  }

  public override void OnEnd(Activity activity)
  {
    foreach (var tag in activity.Tags)
    {
      if (tag.Key == "db.system")
      {
        // Duplicate tag for reporting
        activity.AddTag("db.type", tag.Value);

        // Associate a random error some some redis calls
        if (_random.NextDouble() < REDIS_SPAN_ERROR_RATE)
        {
          activity.AddTag("error", "true");
        }

        break;
      }
    }

    // Change some percentage of the "redis HMSET" spans to represent an external call to another
    // postgres database that does NOT have errors
    Boolean changeToExternalDbSpan = _random.NextDouble() < EXTERNAL_DB_CHANGE_RATE;
    if (
      changeToExternalDbSpan &&
      HasTagValue(activity.Tags, new KeyValuePair<string, string>("db.system", "redis")) && // redis
      activity.DisplayName == "HMSET"                                                       // HMSET
    )
    {
      // Change tags
      activity.SetTag("db.system", "postgres");
      activity.SetTag("db.type", "postgres");
      activity.SetTag("peer.service", EXTERNAL_DB_NAME + ":98321");
      activity.SetTag("error", "false");

      // Change Operation
      activity.DisplayName = "Database.Query";

      // NOTE: Apparently changing the duration is not possible once an Activity has alrady been ended.
      // Calling activity.SetEndTime() from here has no effect on the emitted span duration.
    }
  }

  private static bool HasTagValue(IEnumerable<KeyValuePair<string, string>> tags, KeyValuePair<string, string> tag)
  {
    foreach (KeyValuePair<string, string> possibleTag in tags)
    {
      if (possibleTag.Key == tag.Key && possibleTag.Value == tag.Value)
      {
        return true;
      }
    }
    return false;
  }

}