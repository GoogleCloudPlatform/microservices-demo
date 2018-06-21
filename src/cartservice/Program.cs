using System;
using System.IO;
using cartservice.cartstore;
using CommandLine;
using Grpc.Core;
using Microsoft.Extensions.Configuration;

namespace cartservice
{
    class Program
    {
        const string CART_SERVICE_ADDRESS = "CART_SERVICE_ADDR";
        const string REDIS_ADDRESS = "REDIS_ADDR";

        [Verb("start", HelpText = "Starts the server listening on provided port")]
        class ServerOptions
        {
            [Option('h', "hostname", HelpText = "The ip on which the server is running. If not provided, CART_SERVICE_ADDR environment variable value will be used. If not defined, localhost is used")]
            public string Host { get; set; }

            [Option('p', "port", HelpText = "The port on for running the server", Required = true)]
            public int Port { get; set; }

            [Option('r', "redis", HelpText = "The ip of redis cache")]
            public string Redis { get; set; }

        }

        static object StartServer(string host, int port, string redisAddress)
        {
            var store = new RedisCartStore(redisAddress);
            Server server = new Server
            {
                Services = { Hipstershop.CartService.BindService(new CartServiceImpl(store)) },
                Ports = { new ServerPort(host, port, ServerCredentials.Insecure) }
            };

            Console.WriteLine($"Cart server is listening at {host}:{port}");
            Console.WriteLine("Press any key to stop the server...");
            server.Start();

            Console.ReadKey();

            server.ShutdownAsync().Wait();

            return null;
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
                            string host = options.Host;
                            if (string.IsNullOrEmpty(host))
                            {
                                Console.WriteLine($"Reading host address from {CART_SERVICE_ADDRESS} environment variable...");
                                host = Environment.GetEnvironmentVariable(CART_SERVICE_ADDRESS);
                                if (string.IsNullOrEmpty(host))
                                {
                                    Console.WriteLine("Setting the host to 127.0.0.1");
                                    host = "127.0.0.1";
                                }
                            }

                            string redis = options.Redis;
                            if (string.IsNullOrEmpty(redis))
                            {
                                Console.WriteLine("Reading redis cache address from environment variable");
                                redis = Environment.GetEnvironmentVariable(REDIS_ADDRESS);
                            }
                            return StartServer(host, options.Port, redis);
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
