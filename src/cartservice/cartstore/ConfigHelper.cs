using System;

namespace cartservice.cartstore
{
  internal static class ConfigHelper
  {
    public static bool GetBoolEnvVar(string envVarName, bool defaultValue)
    {
      var varValue = Environment.GetEnvironmentVariable(envVarName) ?? string.Empty;
      var result = varValue.ToLowerInvariant() switch
      {
        "true" or "1" or "yes" =>  true,
        "false" or "0" or "no" =>  false,
        _ => defaultValue
      };

      Console.WriteLine($"{nameof(ConfigHelper)}: env var {envVarName} = {result}");
      return result;
    }
  }
}
