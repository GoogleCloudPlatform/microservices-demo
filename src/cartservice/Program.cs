using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using cartservice.cartstore;
using CommandLine;
using Grpc.Core;
using Microsoft.Extensions.Configuration;

namespace cartservice
{
    class Program
    {
        const string CART_SERVICE_ADDRESS = "LISTEN_ADDR";
        const string REDIS_ADDRESS = "REDIS_ADDR";
        const string CART_SERVICE_PORT = "PORT";

        [Verb("start", HelpText = "Starts the server listening on provided port")]
        class ServerOptions
        {
            [Option('h', "hostname", HelpText = "The ip on which the server is running. If not provided, LISTEN_ADDR environment variable value will be used. If not defined, localhost is used")]
            public string Host { get; set; }

            [Option('p', "port", HelpText = "The port on for running the server")]
            public int Port { get; set; }

            [Option('r', "redis", HelpText = "The ip of redis cache")]
            public string Redis { get; set; }
        }

        static object StartServer(string host, int port, string redisAddress)
        {
            // Run the server in a separate thread and make the main thread busy waiting.
            // The busy wait is because when we run in a container, we can't use techniques such as waiting on user input (Console.Readline())
            Task.Run(() =>
            {
                //var store = new LocalCartStore();
                var store = new RedisCartStore(redisAddress);
                Server server = new Server
                {
                    Services = { Hipstershop.CartService.BindService(new CartServiceImpl(store)) },
                    Ports = { new ServerPort(host, port, ServerCredentials.Insecure) }
                };

                Console.WriteLine($"Cart server is listening at {host}:{port}");
                server.Start();
            });

            // Busy wait to keep the process alive
            while(true)
            {
                Thread.Sleep(TimeSpan.FromMinutes(10));
            }
        }

        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                Console.WriteLine("Invalid number of arguments supplied");
                Environment.Exit(-1);
            }

            switch (args[0])
            {
                case "start":
                    Parser.Default.ParseArguments<ServerOptions>(args).MapResult(
                        (ServerOptions options) => 
                        {
                            // Set hostname/ip address
                            string hostname = options.Host;
                            if (string.IsNullOrEmpty(hostname))
                            {
                                Console.WriteLine($"Reading host address from {CART_SERVICE_ADDRESS} environment variable");
                                hostname = Environment.GetEnvironmentVariable(CART_SERVICE_ADDRESS);
                                if (string.IsNullOrEmpty(hostname))
                                {
                                    Console.WriteLine($"Environment variable {CART_SERVICE_ADDRESS} was not set. Setting the host to 127.0.0.1");
                                    hostname = "127.0.0.1";
                                }
                            }

                            // Set the port
                            int port = options.Port;
                            if (options.Port <= 0)
                            {
                                Console.WriteLine($"Reading cart service port from {CART_SERVICE_PORT} environment variable");
                                string portStr = Environment.GetEnvironmentVariable(CART_SERVICE_PORT);
                                if (string.IsNullOrEmpty(portStr))
                                {
                                    Console.WriteLine($"{CART_SERVICE_PORT} environment variable was not set. Setting the port to 8080");
                                    port = 8080;
                                }
                                else    
                                {
                                    port = int.Parse(portStr);
                                }
                            }

                            // Set redis cache host (hostname+port)
                            string redis = options.Redis;
                            if (string.IsNullOrEmpty(redis))
                            {
                                Console.WriteLine($"Reading redis cache address from environment variable {REDIS_ADDRESS}");
                                redis = Environment.GetEnvironmentVariable(REDIS_ADDRESS);
                                if (string.IsNullOrEmpty(redis))
                                {
                                    Console.WriteLine("Redis cache host(hostname+port) was not specified. It should be specified via command line or REDIS_ADDRESS environment variable.");
                                    return -1;
                                }
                            }

                            return StartServer(hostname, port, redis);
                        },
                        errs => 1);
                    break;
                default:
                    Console.WriteLine("Invalid command");
                    break;
            }
        }
    }
}
