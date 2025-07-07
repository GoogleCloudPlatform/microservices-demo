// Copyright 2024 Google LLC
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
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Grpc.Core;
using MySql.Data.MySqlClient; // This is the new library for MySQL
using Microsoft.Extensions.Logging; // For logging messages

namespace cartservice.cartstore
{
    public class AzureMySQLCartStore : ICartStore
    {
        private readonly string _connectionString;
        private readonly ILogger<AzureMySQLCartStore> _logger;

        // Constructor to initialize with the MySQL connection string and logger
        public AzureMySQLCartStore(string connectionString, ILogger<AzureMySQLCartStore> logger)
        {
            _connectionString = connectionString;
            _logger = logger;
            _logger.LogInformation("AzureMySQLCartStore initialized.");
        }

        public async Task AddItemAsync(string userId, string productId, int quantity)
        {
            _logger.LogInformation($"AddItemAsync called for userId: {userId}, productId: {productId}, quantity: {quantity}");

            try
            {
                using (var connection = new MySqlConnection(_connectionString))
                {
                    await connection.OpenAsync();

                    // Check if the user's cart exists in the Carts table, if not, add it.
                    // This ensures referential integrity for CartItems.
                    using (var cmd = new MySqlCommand("INSERT IGNORE INTO Carts (UserId) VALUES (@UserId)", connection))
                    {
                        cmd.Parameters.AddWithValue("@UserId", userId);
                        await cmd.ExecuteNonQueryAsync();
                    }

                    // Check if the item already exists in the cart for the user
                    using (var checkCmd = new MySqlCommand("SELECT Quantity FROM CartItems WHERE UserId = @UserId AND ProductId = @ProductId", connection))
                    {
                        checkCmd.Parameters.AddWithValue("@UserId", userId);
                        checkCmd.Parameters.AddWithValue("@ProductId", productId);
                        var currentQuantity = await checkCmd.ExecuteScalarAsync();

                        if (currentQuantity != null)
                        {
                            // Update existing item quantity
                            using (var updateCmd = new MySqlCommand("UPDATE CartItems SET Quantity = Quantity + @Quantity WHERE UserId = @UserId AND ProductId = @ProductId", connection))
                            {
                                updateCmd.Parameters.AddWithValue("@Quantity", quantity);
                                updateCmd.Parameters.AddWithValue("@UserId", userId);
                                updateCmd.Parameters.AddWithValue("@ProductId", productId);
                                await updateCmd.ExecuteNonQueryAsync();
                                _logger.LogInformation($"Updated quantity for productId: {productId} in cart for userId: {userId}");
                            }
                        }
                        else
                        {
                            // Add new item to cart
                            using (var insertCmd = new MySqlCommand("INSERT INTO CartItems (UserId, ProductId, Quantity) VALUES (@UserId, @ProductId, @Quantity)", connection))
                            {
                                insertCmd.Parameters.AddWithValue("@UserId", userId);
                                insertCmd.Parameters.AddWithValue("@ProductId", productId);
                                insertCmd.Parameters.AddWithValue("@Quantity", quantity);
                                await insertCmd.ExecuteNonQueryAsync();
                                _logger.LogInformation($"Added new item productId: {productId} with quantity: {quantity} to cart for userId: {userId}");
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error adding item to cart for userId: {userId}");
                throw new RpcException(new Status(StatusCode.Unavailable, $"Can't access cart storage. {ex.Message}"));
            }
        }

        public async Task EmptyCartAsync(string userId)
        {
            _logger.LogInformation($"EmptyCartAsync called with userId: {userId}");

            try
            {
                using (var connection = new MySqlConnection(_connectionString))
                {
                    await connection.OpenAsync();
                    using (var cmd = new MySqlCommand("DELETE FROM CartItems WHERE UserId = @UserId", connection))
                    {
                        cmd.Parameters.AddWithValue("@UserId", userId);
                        await cmd.ExecuteNonQueryAsync();
                        _logger.LogInformation($"Emptied cart for userId: {userId}");
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error emptying cart for userId: {userId}");
                throw new RpcException(new Status(StatusCode.Unavailable, $"Can't access cart storage. {ex.Message}"));
            }
        }

        public async Task<Hipstershop.Cart> GetCartAsync(string userId)
        {
            _logger.LogInformation($"GetCartAsync called for userId: {userId}");
            var cart = new Hipstershop.Cart { UserId = userId };

            try
            {
                using (var connection = new MySqlConnection(_connectionString))
                {
                    await connection.OpenAsync();
                    using (var cmd = new MySqlCommand("SELECT ProductId, Quantity FROM CartItems WHERE UserId = @UserId", connection))
                    {
                        cmd.Parameters.AddWithValue("@UserId", userId);
                        using (var reader = await cmd.ExecuteReaderAsync())
                        {
                            // Get column ordinals (indexes) once for efficiency and compatibility
                            int productIdOrdinal = reader.GetOrdinal("ProductId");
                            int quantityOrdinal = reader.GetOrdinal("Quantity");

                            while (await reader.ReadAsync())
                            {
                                cart.Items.Add(new Hipstershop.CartItem
                                {
                                    ProductId = reader.GetString(productIdOrdinal), // Fixed this line
                                    Quantity = reader.GetInt32(quantityOrdinal)   // Fixed this line
                                });
                            }
                        }
                    }
                }
                _logger.LogInformation($"Retrieved cart for userId: {userId} with {cart.Items.Count} items.");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error getting cart for userId: {userId}");
                throw new RpcException(new Status(StatusCode.Unavailable, $"Can't access cart storage. {ex.Message}"));
            }

            return cart;
        }

        public bool Ping()
        {
            try
            {
                using (var connection = new MySqlConnection(_connectionString))
                {
                    connection.Open();
                    return connection.State == System.Data.ConnectionState.Open;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ping to MySQL database failed.");
                return false;
            }
        }
    }
}