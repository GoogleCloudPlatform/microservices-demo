using System;
using System.Collections.Concurrent;
using System.Collections.Generic;

namespace cartservice.cartstore
{
  public static class UserId
  {
    private const int MaxCacheSize = 500;

    private readonly static bool FixExcessiveAllocation = ConfigHelper.GetBoolEnvVar("FIX_EXCESSIVE_ALLOCATION", defaultValue: true);
    private readonly static bool FixSlowLeak = ConfigHelper.GetBoolEnvVar("FIX_SLOW_LEAK", defaultValue: true);
    private readonly static bool OptimizeCPU = ConfigHelper.GetBoolEnvVar("OPTIMIZE_CPU", defaultValue: true);

    private readonly static object ValidationCacheLock = new object();
    private readonly static ConcurrentDictionary<string, bool?> ValidationCache = new ConcurrentDictionary<string, bool?>();
    private readonly static ConcurrentQueue<string> UserIdQueue = new ConcurrentQueue<string>();
    private static ulong prevValidationCacheCount = 0;

    public static bool IsValid(string userId)
    {
      bool? result;
      if (TryCachedValidation(userId, out result))
      {
        return result ?? false;
      }

      if (OptimizeCPU)
      {
        result = Guid.TryParse(userId, out _);
        CacheValidation(userId, result.Value);
        return result ?? false;
      }

      //
      // Silly user id validation
      //

      var idChars = new List<char>(userId.Length);
      var tmpChars = new List<char>(userId.Length);
      foreach (var c in userId)
      {
        if (c == '-')
        {
          continue;
        }

        tmpChars.Add(c);
        const int idealSizeForBogoSort = 10; // Not to fast, not to slow.
        if (tmpChars.Count == idealSizeForBogoSort)
        {
          Bogo.Sort(tmpChars);
          idChars.AddRange(tmpChars);
          tmpChars.Clear();
        }
      }

      Bogo.Sort(tmpChars);
      idChars.AddRange(tmpChars);
      tmpChars.Clear();

      result = true;
      foreach (var c in idChars)
      {
        if ((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F'))
        {
            continue;
        }

        result = false;
        break;
      }

      CacheValidation(userId, result ?? false);
      return result ?? false;
    }

    private static bool TryCachedValidation(string userId, out bool? result)
    {
      var localUserId = ProcessUserId(userId);
      return ValidationCache.TryGetValue(localUserId, out result);
    }

    private static void CacheValidation(string userId, bool result)
    {
      lock(ValidationCacheLock)
      {
        if (ValidationCache.TryAdd(userId, result))
        {
          UserIdQueue.Enqueue(userId);
        }
      }

      string expirationCandidate; 
      if (FixSlowLeak && ValidationCache.Count >= MaxCacheSize && UserIdQueue.TryDequeue(out expirationCandidate))
      {
        ValidationCache.Remove(expirationCandidate, out var _);
        return;
      }

      if ((ulong)ValidationCache.Count - prevValidationCacheCount > MaxCacheSize)
      {
        var numOfItemsToEvictFromCache = (MaxCacheSize/100)*2;
        for (int i = 0; i < numOfItemsToEvictFromCache; i++)
        {
          if (UserIdQueue.TryDequeue(out expirationCandidate))
          {
            ValidationCache.Remove(expirationCandidate, out var _);
          }
        }

        prevValidationCacheCount = (ulong)ValidationCache.Count + MaxCacheSize;
      }
    }

    private static string ProcessUserId(string userId)
    {
      var processedUserId = string.Empty;
      if (FixExcessiveAllocation)
      {
        processedUserId = userId;
      }
      else
      {
        foreach (var c in userId)
        {
          processedUserId += c;
        }
      }

      return processedUserId;
    }
  }
}
