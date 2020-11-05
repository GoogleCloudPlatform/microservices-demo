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
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using cartservice.cartstore;
using cartservice.interfaces;
using CommandLine;
using Grpc.Core;
using Microsoft.Extensions.Configuration;
using OpenCensus.Exporter.Stackdriver;
using OpenCensus.Trace;

namespace cartservice
{
    class Program
    {
        const string CART_SERVICE_ADDRESS = "LISTEN_ADDR";
        const string REDIS_ADDRESS = "REDIS_ADDR";
        const string CART_SERVICE_PORT = "PORT";

        const string PROJECT_ID = "PROJECT_ID";

        [Verb("start", HelpText = "Starts the server listening on provided port")]
        class ServerOptions
        {
            [Option('h', "hostname", HelpText = "The ip on which the server is running. If not provided, LISTEN_ADDR environment variable value will be used. If not defined, localhost is used")]
            public string Host { get; set; }

            [Option('p', "port", HelpText = "The port on for running the server")]
            public int Port { get; set; }

            [Option('r', "redis", HelpText = "The ip of redis cache")]
            public string Redis { get; set; }

            [Option("projectId", HelpText = "The ProjectId to which telemetry will flow")]
            public string ProjectId { get; set; }
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
                            string hostname = ReadParameter("host address", options.Host, CART_SERVICE_ADDRESS, p => p, "0.0.0.0");

                            // Set the port
                            int port = ReadParameter("cart service port", options.Port, CART_SERVICE_PORT, int.Parse, 8080);

                            string projectId = ReadParameter("cloud service project id", options.ProjectId, PROJECT_ID, p => p, null);

                            // Initialize Stackdriver Exporter - currently for tracing only
                            if (!string.IsNullOrEmpty(projectId))
                            {
                                var exporter = new StackdriverExporter(
                                    projectId, 
                                    Tracing.ExportComponent,
                                    viewManager: null);
                                exporter.Start();
                            }

                            // Set redis cache host (hostname+port)
                            string redis = ReadParameter("redis cache address", options.Redis, REDIS_ADDRESS, p => p, null);

                            ICartStore cartStore = InstrumentedCartStore.Create(redis);
                            return StartServer(hostname, port, cartStore);
                        },
                        errs => 1);
                    break;
                default:
                    Console.WriteLine("Invalid command");
                    break;
            }
        }

        /// <summary>
        /// Reads parameter in the right order
        /// </summary>
        /// <param name="description">Parameter description</param>
        /// <param name="commandLineValue">Value provided from the command line</param>
        /// <param name="environmentVariableName">The name of environment variable where it could have been set</param>
        /// <param name="environmentParser">The method that parses environment variable and returns typed parameter value</param>
        /// <param name="defaultValue">Parameter's default value - in case other method failed to assign a value</param>
        /// <typeparam name="T">The type of the parameter</typeparam>
        /// <returns>Parameter value read from all the sources in the right order(priorities)</returns>
        private static T ReadParameter<T>(
            string description,
            T commandLineValue, 
            string environmentVariableName, 
            Func<string, T> environmentParser, 
            T defaultValue)
        {
            // Command line argument
            if(!EqualityComparer<T>.Default.Equals(commandLineValue, default(T))) 
            {
                return commandLineValue;
            }

            // Environment variable
            Console.Write($"Reading {description} from environment variable {environmentVariableName}. ");
            string envValue = Environment.GetEnvironmentVariable(environmentVariableName);
            if (!string.IsNullOrEmpty(envValue))
            {
                try
                {
                    var envTyped = environmentParser(envValue);
                    Console.WriteLine("Done!");
                    return envTyped;
                }
                catch (Exception)
                {
                    // We assign the default value later on
                }
            }

            Console.WriteLine($"Environment variable {environmentVariableName} was not set. Setting {description} to {defaultValue}");
            return defaultValue;
        }
    }
}
