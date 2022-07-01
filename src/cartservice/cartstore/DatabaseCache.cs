using System;
using System.Threading;
using System.Threading.Tasks;
using StackExchange.Redis;

namespace cartservice.cartstore
{
  public class DatabaseCache
  {
    private static readonly bool OptimizeBlocking = ConfigHelper.GetBoolEnvVar("OPTIMIZE_BLOCKING", defaultValue: true);

    private readonly ConnectionMultiplexer _conn;
    private readonly Semaphore _pool;

    public DatabaseCache(ConnectionMultiplexer connection)
    {
      _conn = connection;

      var maxConcurrentDBRetrieval = OptimizeBlocking ? Environment.ProcessorCount : 1;
      _pool = new Semaphore(0, maxConcurrentDBRetrieval);
      _pool.Release(maxConcurrentDBRetrieval);
    }

    public IDatabase ByPassBlocking() => _conn.GetDatabase();

    public IDatabase Get()
    {
      _pool.WaitOne();
      if (OptimizeBlocking)
      {
        _pool.Release(1);
      }
      else
      {
        Task.Run(async () =>
        {
            await Task.Delay(Random.Shared.Next(250, 750));
            _pool.Release(1);
        });
      }

      return _conn.GetDatabase();
    }
  }
}
