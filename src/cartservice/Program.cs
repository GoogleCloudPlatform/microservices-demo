using System;
using CommandLine;
using Grpc.Core;

namespace cartservice
{
    class Program
    {
        [Verb("start", HelpText = "Starts the server listening on provided port")]
        class ServerOptions
        {

            [Option('p', "port", HelpText = "The port on for running the server", Required = true)]
            public int Port { get; set; }
        }

        static object StartServer(string host, int port)
        {
            var store = new CartStore();
            Server server = new Server
            {
                Services = { Hipstershop.CartService.BindService(new CartServiceImpl(store)) },
                Ports = { new ServerPort(host, port, ServerCredentials.Insecure) }
            };

            Console.WriteLine("Cart server is listening on port " + port);
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
                        (ServerOptions options) => StartServer("localhost", options.Port),
                        errs => 1);
                    break;
                default:
                    Console.WriteLine("Invalid command");
                    break;
            }

            Console.WriteLine("Hello World!");
        }
    }
}
