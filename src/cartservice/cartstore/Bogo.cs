using System;
using System.Collections.Generic;

namespace cartservice.cartstore
{
  public static class Bogo
  {
    public static void Sort(List<char> list)
    {
      do 
      {
        Shuffle(list);
      } while (!IsSorted(list));
    }

    private static void Shuffle(List<char> list)
    {
      var r = Random.Shared;
      for (int i = 0; i < list.Count; i++)
      {
        var k = r.Next(i, list.Count);
        var tmp = list[k];
        list[k] = list[i];
        list[i] = tmp;
      }
    }

    private static bool IsSorted(List<char> list)
    {
      if (list is null || list.Count <= 1)
      {
        return true;
      }

      var prevChar = list[0];
      for (int i = 1; i < list.Count; i++)
      {
        var currChar = list[i];
        if (prevChar > currChar)
        {
          return false;
        }

        prevChar = currChar;
      }

      return true;
    }
  }
}
