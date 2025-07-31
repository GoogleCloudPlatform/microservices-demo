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
using Google.Cloud.Spanner.Data;
using Grpc.Core;
using Microsoft.Extensions.Configuration;
using System.Threading.Tasks;

namespace cartservice.cartstore
{
    public class SpannerCartStore : ICartStore
    {
        private static readonly string TableName = "CartItems";
        private static readonly string DefaultInstanceName = "onlineboutique";
        private static readonly string DefaultDatabaseName = "carts";
        private readonly string databaseString;

        public SpannerCartStore(IConfiguration configuration)
        {
            string spannerProjectId = configuration["SPANNER_PROJECT"];
            string spannerInstanceId = configuration["SPANNER_INSTANCE"];
            string spannerDatabaseId = configuration["SPANNER_DATABASE"];
            string spannerConnectionString = configuration["SPANNER_CONNECTION_STRING"];
            SpannerConnectionStringBuilder builder = new();
            if (!string.IsNullOrEmpty(spannerConnectionString)) {
                builder.DataSource = spannerConnectionString;
                databaseString = builder.ToString();
                Console.WriteLine($"Spanner connection string: ${databaseString}");
                return;
            }
            if (string.IsNullOrEmpty(spannerInstanceId))
                spannerInstanceId = DefaultInstanceName;
            if (string.IsNullOrEmpty(spannerDatabaseId))
                spannerDatabaseId = DefaultDatabaseName;
            builder.DataSource =
                $"projects/{spannerProjectId}/instances/{spannerInstanceId}/databases/{spannerDatabaseId}";
            databaseString = builder.ToString();
            Console.WriteLine($"Built Spanner connection string: '{databaseString}'");
        }


        public async Task AddItemAsync(string userId, string productId, int quantity)
        {
            Console.WriteLine($"AddItemAsync for {userId} called");
            try
            {
                using SpannerConnection spannerConnection = new(databaseString);
                await spannerConnection.RunWithRetriableTransactionAsync(async transaction =>
                {
                    int currentQuantity = 0;
                    var quantityLookup = spannerConnection.CreateSelectCommand(
                        $"SELECT * FROM {TableName} WHERE userId = @userId AND productId = @productId",
                        new SpannerParameterCollection
                        {
                            { "userId", SpannerDbType.String },
                            { "productId", SpannerDbType.String }
                        });
                    quantityLookup.Parameters["userId"].Value = userId;
                    quantityLookup.Parameters["productId"].Value = productId;
                    quantityLookup.Transaction = transaction;
                    using (var reader = await quantityLookup.ExecuteReaderAsync())
                    {
                        while (await reader.ReadAsync()) {
                            currentQuantity += reader.GetFieldValue<int>("quantity");
                        }
                    }

                    var cmd = spannerConnection.CreateInsertOrUpdateCommand(TableName,
                        new SpannerParameterCollection
                        {
                            { "userId", SpannerDbType.String },
                            { "productId", SpannerDbType.String },
                            { "quantity", SpannerDbType.Int64 }
                        });
                    cmd.Parameters["userId"].Value = userId;
                    cmd.Parameters["productId"].Value = productId;
                    cmd.Parameters["quantity"].Value = currentQuantity + quantity;
                    cmd.Transaction = transaction;
                    await Task.Run(() =>
                    {
                        return cmd.ExecuteNonQueryAsync();
                    });
                });
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
            try
            {
                using SpannerConnection spannerConnection = new(databaseString);
                var cmd = spannerConnection.CreateSelectCommand(
                    $"SELECT * FROM {TableName} WHERE userId = @userId",
                    new SpannerParameterCollection {
                        { "userId", SpannerDbType.String }
                    }
                );
                cmd.Parameters["userId"].Value = userId;
                using var reader = await cmd.ExecuteReaderAsync();
                while (await reader.ReadAsync())
                {
                    // Only add the userId if something is in the cart.
                    // This is based on how the cartservice example behaves.
                    // An empty cart has no userId attached.
                    cart.UserId = userId;

                    Hipstershop.CartItem item = new()
                    {
                        ProductId = reader.GetFieldValue<string>("productId"),
                        Quantity = reader.GetFieldValue<int>("quantity")
                    };
                    cart.Items.Add(item);
                }

                return cart;
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
                using SpannerConnection spannerConnection = new(databaseString);
                await Task.Run(() =>
                {
                    var cmd = spannerConnection.CreateDmlCommand(
                        $"DELETE FROM {TableName} WHERE userId = @userId",
                    new SpannerParameterCollection
                    {
                        { "userId", SpannerDbType.String }
                    });
                    cmd.Parameters["userId"].Value = userId;
                    return cmd.ExecuteNonQueryAsync();
                });
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

