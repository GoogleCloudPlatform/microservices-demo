// Copyright 2018 Google LLC
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

﻿using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using cartservice.cartstore;
using cartservice.interfaces;
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

        static object StartServer(string host, int port, ICartStore cartStore)
        {
            // Run the server in a separate thread and make the main thread busy waiting.
            // The busy wait is because when we run in a container, we can't use techniques such as waiting on user input (Console.Readline())
            Task serverTask = Task.Run(async () =>
            {
                try
                {
                    await cartStore.InitializeAsync();

                    Console.WriteLine($"Trying to start a grpc server at  {host}:{port}");
                    Server server = new Server
                    {
                        Services =
                        {
                            // Cart Service Endpoint
                             Hipstershop.CartService.BindService(new CartServiceImpl(cartStore)),

                             // Health Endpoint
                             Grpc.Health.V1.Health.BindService(new HealthImpl(cartStore))
                        },
                        Ports = { new ServerPort(host, port, ServerCredentials.Insecure) }
                    };

                    Console.WriteLine($"Cart server is listening at {host}:{port}");
                    server.Start();

                    Console.WriteLine("Initialization completed");

                    // Keep the server up and running
                    while(true)
                    {
                        Thread.Sleep(TimeSpan.FromMinutes(10));
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex);
                }
            });

            return Task.WaitAny(new[] { serverTask });
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
                            Console.WriteLine($"Started as process with id {System.Diagnostics.Process.GetCurrentProcess().Id}");

                            // Set hostname/ip address
                            string hostname = options.Host;
                            if (string.IsNullOrEmpty(hostname))
                            {
                                Console.WriteLine($"Reading host address from {CART_SERVICE_ADDRESS} environment variable");
                                hostname = Environment.GetEnvironmentVariable(CART_SERVICE_ADDRESS);
                                if (string.IsNullOrEmpty(hostname))
                                {
                                    Console.WriteLine($"Environment variable {CART_SERVICE_ADDRESS} was not set. Setting the host to 0.0.0.0");
                                    hostname = "0.0.0.0";
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
                            ICartStore cartStore;
                            string redis = ReadRedisAddress(options.Redis);

                            // Redis was specified via command line or environment variable
                            if (!string.IsNullOrEmpty(redis))
                            {
                                // If you want to start cart store using local cache in process, you can replace the following line with this:
                                // cartStore = new LocalCartStore();
                                cartStore = new RedisCartStore(redis);

                                return StartServer(hostname, port, cartStore);
                            }
                            else
                            {
                                Console.WriteLine("Redis cache host(hostname+port) was not specified. Starting a cart service using local store");
                                Console.WriteLine("If you wanted to use Redis Cache as a backup store, you should provide its address via command line or REDIS_ADDRESS environment variable.");
                                cartStore = new LocalCartStore();
                            }

                            return StartServer(hostname, port, cartStore);
                        },
                        errs => 1);
                    break;
                default:
                    Console.WriteLine("Invalid command");
                    break;
            }
        }

        private static string ReadRedisAddress(string address)
        {
            if (!string.IsNullOrEmpty(address))
            {
                return address;
            }

            Console.WriteLine($"Reading redis cache address from environment variable {REDIS_ADDRESS}");
            string redis = Environment.GetEnvironmentVariable(REDIS_ADDRESS);
            if (!string.IsNullOrEmpty(redis))
            {
                return redis;
            }

            return null;
        }
    }
}
