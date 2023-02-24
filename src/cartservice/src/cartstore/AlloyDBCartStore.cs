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
using Npgsql;
using Microsoft.Extensions.Configuration;
using System.Threading.Tasks;

namespace cartservice.cartstore
{
    public class AlloyDBCartStore : ICartStore
    {
        private readonly string tableName;
        private readonly string connectionString;

        public SpannerCartStore(IConfiguration configuration)
        {
            Console.WriteLine("TEST");
            // TODO: Don't use passwords in the environment. We should be using KMS
            string alloyDBPassword = configuration["PGPASSWORD"];
            // TODO: Create a separate user for connecting within the application
            // rather than using our superuser
            string alloyDBUser = "postgres";
            string databaseName = configuration["ALLOYDB_DATABASE_NAME"];
            // TODO: Consider splitting workloads into read vs. write and take
            // advantage of the AlloyDB read pools
            string primaryIPAddress = configuration["ALLOYDB_PRIMARY_IP"];
            connectionString = "Host="          +
                               primaryIPAddress +
                               ";Username="     +
                               alloyDBUser      +
                               ";Password="     +
                               alloyDBPassword  +
                               ";Database="     +
                               databaseName;
            Console.WriteLine($"Built AlloyDB primary instance connection string: '{connectionString}'");

            tableName = configuration["ALLOYDB_TABLE_NAME"];
        }


        public async Task AddItemAsync(string userId, string productId, int quantity)
        {
            Console.WriteLine($"AddItemAsync for {userId} called");
            try
            {
                await using var dataSource = NpgsqlDataSource.Create(connectionString);

                // Fetch the current quantity for our userId/productId tuple
                var fetchCmd = $"SELECT quantity FROM {tableName} WHERE userID='{userId}' AND productID='{productId}'";
                await using (var cmd = dataSource.CreateCommand(fetchCmd)
                await using (var reader = await cmd.ExecuteReaderAsync())
                {
                    currentQuantity = "";
                    while (await reader.ReadAsync())
                        currentQuantity += reader.GetString(0);
                }
                var totalQuantity = quantity + currentQuantity;

                var insertCmd = $"INSERT INTO {tableName} (userId, productId, quantity) VALUES ({us    erId}, {productId}, {totalQuantity})";
                await using (var cmd = dataSource.CreateCommand(insertCmd)
                {
                    return await cmd.ExecuteNonQueryAsync();
                }
            }
            catch (Exception ex)
            {
                throw new RpcException(
                    new Status(StatusCode.FailedPrecondition, $"Can't access cart storage at {databaseString}. {ex}"));
            }
        }


        public async Task<Hipstershop.Cart> GetCartAsync(string userId)
        {
            Console.WriteLine($"GetCartAsync called for userId={userId}");
            Hipstershop.Cart cart = new();
            cart.UserId = userId;
            try
            {
                await using var dataSource = NpgsqlDataSource.Create(connectionString);
                var cartFetchCmd = $"SELECT productId, quantity FROM {tableName} WHERE userId = '{userId}'";
                await using (var cmd = dataSource.CreateCommand(cartFetchCmd);
                await using (var reader = await cmd.ExecutReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        Hipstership.CartItem item = new()
                        {
                            ProductId = reader.GetString(0);
                            Quantity = reader.GetString(1);
                        }
                        cart.Items.Add(item);
                    }
                    return cart;
                }
            }
            catch (Exception ex)
            {
                throw new RpcException(
                    new Status(StatusCode.FailedPrecondition, $"Can't access cart storage at {databaseString}. {ex}"));
            }
        }


        public async Task EmptyCartAsync(string userId)
        {
            Console.WriteLine($"EmptyCartAsync called for userId={userId}");

            try
            {
                await using var dataSource = NpgsqlDataSource.Create(connectionString);
                var deleteCmd = $"DELETE FROM {tableName} WHERE userID = userId";
                await using (var cmd = dataSource.CreateCommand(deleteCmd)
                {
                    return await cmd.ExecuteNonQueryAsync();
                }
            }
            catch (Exception ex)
            {
                throw new RpcException(
                    new Status(StatusCode.FailedPrecondition, $"Can't access cart storage at {databaseString}. {ex}"));
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

