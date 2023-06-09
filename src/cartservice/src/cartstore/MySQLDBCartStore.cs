// Copyright 2021 Google LLC
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

using System;
using Grpc.Core;
// using MySql.Data.MySqlClient;
using MySqlConnector;
using Microsoft.Extensions.Configuration;
using System.Threading.Tasks;

namespace cartservice.cartstore
{
    public class MySQLDBCartStore : ICartStore
    {
        private readonly string tableName;
        private readonly string connectionString;

        public MySQLDBCartStore(IConfiguration configuration)
        {
            string mysqlDBHost = configuration["MYSQL_HOST"];
            string mysqlDBPort = configuration["MYSQL_PORT"];
            string mysqlDBPassword = configuration["MYSQL_PASSWORD"];
            string mysqlDBUser = configuration["MYSQL_USERNAME"];;
            string databaseName = configuration["MYSQL_DATABASE"];
            connectionString = "server="        +
                               mysqlDBHost      +
                               ";port="         +
                               mysqlDBPort      +
                               ";uid="          +
                               mysqlDBUser      +
                               ";pwd="          +
                               mysqlDBPassword  +
                               ";database="     +
                               databaseName;

            //DEBUG
            // connectionString = "server=172.20.44.149;port=3306;uid=root;pwd=my-secret-pw;database=mysql";

            Console.WriteLine(connectionString);

            //DEBUG
            // try
            // {
            //     await using var connection = new MySqlConnection(connectionString);
            //     connection.Open();

            //     var stm = "SELECT VERSION()";
            //     var cmd = new MySqlCommand(stm, connection);

            //     var version = cmd.ExecuteScalar().ToString();
            //     Console.WriteLine($"MySQL version: {version}");
            // }
            // catch (Exception ex)
            // {
            //     throw new RpcException(
            //         new Status(StatusCode.FailedPrecondition, $"Can't access cart storage at {connectionString}. {ex}"));
            // }

            tableName = configuration["MYSQL_TABLE"];
        }


        public async Task AddItemAsync(string userId, string productId, int quantity)
        {
            Console.WriteLine($"AddItemAsync for {userId} called");
            try
            {

                await using var connection = new MySqlConnection(connectionString);
                connection.Open();

                // Fetch the current quantity for our userId/productId tuple
                var fetchCmd = $"SELECT quantity FROM {tableName} WHERE userID='{userId}' AND productID='{productId}'";
                var currentQuantity = 0;
                var cmdRead = new MySqlCommand(fetchCmd, connection);
                await using (var reader = await cmdRead.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                        currentQuantity += reader.GetInt32(0);
                }
                var totalQuantity = quantity + currentQuantity;

                var insertCmd = $"INSERT INTO {tableName} (userId, productId, quantity) VALUES ('{userId}', '{productId}', {totalQuantity})";
                await using (var cmdInsert = new MySqlCommand(insertCmd, connection))
                {
                    await Task.Run(() =>
                    {
                        return cmdInsert.ExecuteNonQueryAsync();
                    });
                }
            }
            catch (Exception ex)
            {
                throw new RpcException(
                    new Status(StatusCode.FailedPrecondition, $"Can't access cart storage at {connectionString}. {ex}"));
            }
        }


        public async Task<Hipstershop.Cart> GetCartAsync(string userId)
        {
            Console.WriteLine($"GetCartAsync called for userId={userId}");
            Hipstershop.Cart cart = new();
            cart.UserId = userId;
            try
            {
                await using var connection = new MySqlConnection(connectionString);
                connection.Open();

                var cartFetchCmd = $"SELECT productId, quantity FROM {tableName} WHERE userId = '{userId}'";
                var cmd = new MySqlCommand(cartFetchCmd, connection);
                await using (var reader = await cmd.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        Hipstershop.CartItem item = new()
                        {
                            ProductId = reader.GetString(0),
                            Quantity = reader.GetInt32(1)
                        };
                        cart.Items.Add(item);
                    }
                }
                await Task.Run(() =>
                {
                    return cart;
                });
            }
            catch (Exception ex)
            {
                throw new RpcException(
                    new Status(StatusCode.FailedPrecondition, $"Can't access cart storage at {connectionString}. {ex}"));
            }
            return cart;
        }


        public async Task EmptyCartAsync(string userId)
        {
            Console.WriteLine($"EmptyCartAsync called for userId={userId}");

            try
            {
                await using var connection = new MySqlConnection(connectionString);
                connection.Open();

                var deleteCmd = $"DELETE FROM {tableName} WHERE userID = '{userId}'";
                await using (var cmd = new MySqlCommand(deleteCmd, connection))
                {
                    await Task.Run(() =>
                    {
                        return cmd.ExecuteNonQueryAsync();
                    });
                }
            }
            catch (Exception ex)
            {
                throw new RpcException(
                    new Status(StatusCode.FailedPrecondition, $"Can't access cart storage at {connectionString}. {ex}"));
            }
        }

        public bool Ping()
        {
            try
            {
                return true;
            }
            catch (Exception)
            {
                return false;
            }
        }
    }
}

