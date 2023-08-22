#include <iostream>
#include <stdio.h>
#include <libpq-fe.h>

PGconn *getDatabaseConnection() {
  // Get the environment variables.
  const char *user = getenv("POSTGRES_USER");
  const char *password = getenv("POSTGRES_PASSWORD");
  const char *database = getenv("POSTGRES_DATABASE");
  const char *host = getenv("POSTGRES_HOST");

  // Create the connection string using a formatted string.
  const char *connectionString =
    "host=%s dbname=%s user=%s password=%s";
  char formattedConnectionString[256]; // Adjust the buffer size as needed.
  snprintf(formattedConnectionString, sizeof(formattedConnectionString),
           connectionString, host, database, user, password);

  // Create a connection object.
  PGconn *conn = PQconnectdb(connectionString);

  // Check if the connection was successful.
  if (PQstatus(conn) != CONNECTION_OK) {
    // The connection failed.
    std::cerr << "Failed to connect to database: " << PQerrorMessage(conn) << std::endl;
    PQfinish(conn);
    return NULL;
  }

  // The connection was successful.
  return conn;
}
