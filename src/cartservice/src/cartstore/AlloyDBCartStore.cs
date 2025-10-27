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
using Npgsql;
using Microsoft.Extensions.Configuration;
using System.Threading.Tasks;
using Google.Api.Gax.ResourceNames;
using Google.Cloud.SecretManager.V1;
 
namespace cartservice.cartstore
{
    public class AlloyDBCartStore : ICartStore
    {
        private readonly string tableName;
        private readonly string connectionString;

        public AlloyDBCartStore(IConfiguration configuration)
        {
            // Create a Cloud Secrets client.
            SecretManagerServiceClient client = SecretManagerServiceClient.Create();
            var projectId = configuration["PROJECT_ID"];
            var secretId = configuration["ALLOYDB_SECRET_NAME"];
            SecretVersionName secretVersionName = new SecretVersionName(projectId, secretId, "latest");

            AccessSecretVersionResponse result = client.AccessSecretVersion(secretVersionName);
            // Convert the payload to a string. Payloads are bytes by default.
            string alloyDBPassword = result.Payload.Data.ToStringUtf8().TrimEnd('\r', '\n');
        
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

            tableName = configuration["ALLOYDB_TABLE_NAME"];
        }


    public async Task AddItemAsync(string userId, string productId, int quantity)
    {
        Console.WriteLine($"AddItemAsync for {userId} called");
        try
        {
            await using var dataSource = NpgsqlDataSource.Create(connectionString);

            var fetchCmd = $"SELECT quantity FROM {tableName} WHERE userID='{userId}' AND productID='{productId}'";
            var currentQuantity = 0;
            var cmdRead = dataSource.CreateCommand(fetchCmd);
            await using (var reader = await cmdRead.ExecuteReaderAsync())
            {
                while (await reader.ReadAsync())
                    currentQuantity += reader.GetInt32(0);
            }

            var totalQuantity = quantity + currentQuantity;

            // Use INSERT ... ON CONFLICT to prevent duplicate key error
            var insertCmd = $@"
                INSERT INTO {tableName} (userId, productId, quantity)
                VALUES ('{userId}', '{productId}', {totalQuantity})
                ON CONFLICT (userId, productId)
                DO UPDATE SET quantity = {totalQuantity};
            ";

            await using (var cmdInsert = dataSource.CreateCommand(insertCmd))
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
                new Status(StatusCode.FailedPrecondition, $"Unable to access cart storage due to an internal error. {ex}"));
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
                var cmd = dataSource.CreateCommand(cartFetchCmd);
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
                    new Status(StatusCode.FailedPrecondition, $"Unable to access cart storage due to an internal error. {ex}"));
            }
            return cart;
        }


        public async Task EmptyCartAsync(string userId)
        {
            Console.WriteLine($"EmptyCartAsync called for userId={userId}");

            try
            {
                await using var dataSource = NpgsqlDataSource.Create(connectionString);
                var deleteCmd = $"DELETE FROM {tableName} WHERE userID = '{userId}'";
                await using (var cmd = dataSource.CreateCommand(deleteCmd))
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
                    new Status(StatusCode.FailedPrecondition, $"Unable to access cart storage due to an internal error. {ex}"));
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

