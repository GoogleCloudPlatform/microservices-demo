using System;

namespace cartservice.cartstore
{
  internal static class ConfigHelper
  {
    public static bool GetBoolEnvVar(string envVarName, bool defaultValue)
    {
      var varValue = Environment.GetEnvironmentVariable(envVarName) ?? string.Empty;
      return varValue.ToLowerInvariant() switch
      {
        "true" or "1" or "yes" =>  true,
        _ => defaultValue
      };
    }
  }
}
