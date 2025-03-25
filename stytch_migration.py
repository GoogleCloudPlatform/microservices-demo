import os
import mysql.connector
from dotenv import load_dotenv
import re
from stytch import B2BClient
from stytch.b2b.models.organizations import SearchQuery, SearchQueryOperator
from stytch.b2b.models.passwords import MigrateRequestHashType

# Load environment variables
load_dotenv()

# Stytch configuration
STYTCH_PROJECT_ID = os.getenv('STYTCH_PROJECT_ID')
STYTCH_SECRET = os.getenv('STYTCH_SECRET')

# MySQL configuration
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Initialize Stytch client
stytch_client = B2BClient(
    project_id=STYTCH_PROJECT_ID,
    secret=STYTCH_SECRET,
)


def connect_to_mysql():
    """Connect to MySQL database and return connection object"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        print(f"Connected to MySQL database: {DB_NAME}")
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        raise


def fetch_clients(conn):
    """Fetch all clients from the client table"""
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, client_name FROM client")
        clients = cursor.fetchall()
        print(f"Fetched {len(clients)} clients from database")
        return clients
    except mysql.connector.Error as err:
        print(f"Error fetching clients: {err}")
        raise
    finally:
        cursor.close()


def fetch_users_for_client(conn, client_id):
    """Fetch all users for a specific client, including group associations"""
    cursor = conn.cursor(dictionary=True)

    try:
        # Query that gets users associated directly with the client
        # AND users associated through groups
        query = """
            SELECT DISTINCT u.id, u.username, u.password_hash
            FROM user u
            WHERE 
                -- Direct association through user_client
                u.id IN (
                    SELECT user_id 
                    FROM user_client 
                    WHERE client_id = %s
                )
                -- Group-based association
                OR u.id IN (
                    SELECT gu.user_id
                    FROM group_user gu
                    JOIN group_client gc ON gu.group_id = gc.group_id
                    WHERE gc.client_id = %s
                )
        """
        cursor.execute(query, (client_id, client_id))
        users = cursor.fetchall()
        print(
            f"Fetched {len(users)} users for client ID {client_id} (including group associations)")
        return users
    except mysql.connector.Error as err:
        print(f"Error fetching users for client {client_id}: {err}")
        raise
    finally:
        cursor.close()


def clean_name(name):
    """Clean a name by removing special characters and spaces"""
    return re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-'))


def create_organization(client_name, client_id):
    """Create a Stytch organization for a client"""
    try:
        # Generate a slug from the client name
        org_slug = clean_name(client_name)

        # Create the organization
        resp = stytch_client.organizations.create(
            organization_name=client_name,
            organization_slug=f"{org_slug}-{client_id}",
        )

        # Extract the organization_id from the response
        organization_id = resp.organization.organization_id

        print(
            f"Created organization for {client_name} with ID: {organization_id}")
        return organization_id
    except Exception as e:
        print(f"Error creating organization for {client_name}: {e}")
        return None


def find_organization_by_slug(slug):
    """Try to find an organization by its slug"""
    try:
        # Search for the organization by slug
        resp = stytch_client.organizations.search(
            query=SearchQuery(
                limit=1,  # We only need one result for an exact match
                operator=SearchQueryOperator.OR,
                operands=[
                    {
                        'filter_name': "organization_slugs",
                        'filter_value': [slug],
                    },
                ],
            ),
        )

        # If we have any results, return the ID of the first one
        if resp.organizations and len(resp.organizations) > 0:
            org_id = resp.organizations[0].organization_id
            print(f"Found organization with slug '{slug}': {org_id}")
            return org_id

        print(f"No organization found with slug '{slug}'")
        return None
    except Exception as e:
        print(f"Error searching for organization by slug {slug}: {e}")
        return None


def add_user_to_organization(organization_id, username, trusted_metadata, password_hash=None):
    """Add a user to a Stytch organization"""
    try:
        # Create the member
        resp = stytch_client.organizations.members.create(
            organization_id=organization_id,
            email_address=username,
            trusted_metadata=trusted_metadata,
        )
        member_id = resp.member_id
        print(
            f"Added user {username} to organization {organization_id}, member ID: {member_id}")

        # If password hash is provided, migrate it
        if password_hash and password_hash.startswith('$2'):
            migrate_password(username, password_hash, organization_id)
        elif password_hash:
            print(
                f"Skipping password migration for {username} - invalid bcrypt hash format")

        return member_id
    except Exception as e:
        print(
            f"Error adding user {username} to organization {organization_id}: {e}")
        return None


def migrate_password(email_address, password_hash, organization_id):
    """Migrate a user's password hash to Stytch"""
    try:
        # Migrate the password
        resp = stytch_client.passwords.migrate(
            email_address=email_address,
            hash=password_hash,
            hash_type=MigrateRequestHashType.BCRYPT,
            organization_id=organization_id,
        )

        print(f"Migrated password for user {email_address}")
        return True
    except Exception as e:
        print(f"Error migrating password for user {email_address}: {e}")
        return False


def fetch_user_roles(conn, user_id):
    """Fetch all roles for a specific user"""
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT r.name 
            FROM role r
            JOIN user_role ur ON r.id = ur.role_id
            WHERE ur.user_id = %s
        """
        cursor.execute(query, (user_id,))
        roles = cursor.fetchall()
        role_names = [role['name'] for role in roles]
        print(
            f"Fetched {len(role_names)} roles for user ID {user_id}: {', '.join(role_names)}")
        return role_names
    except mysql.connector.Error as err:
        print(f"Error fetching roles for user {user_id}: {err}")
        return [""]  # Return an empty list on error
    finally:
        cursor.close()


def main():
    # Connect to MySQL
    conn = connect_to_mysql()

    try:
        # Fetch all clients
        clients = fetch_clients(conn)

        client_org_mapping = {}

        # Process each client
        for client in clients:
            client_id = client['id']
            client_name = client['client_name']

            # Skip clients with "deleted" in their name
            if "deleted" in client_name.lower():
                print(
                    f"Skipping deleted client: {client_name} (ID: {client_id})")
                continue

            print(f"\nProcessing client: {client_name} (ID: {client_id})")

            # Check if organization already exists
            org_slug = clean_name(client_name)
            print(
                f"Checking for organization with slug: {org_slug}-{client_id}")
            organization_id = find_organization_by_slug(
                f"{org_slug}-{client_id}")

            if not organization_id:
                # Create new organization
                organization_id = create_organization(client_name, client_id)
                if not organization_id:
                    print(
                        f"Skipping client {client_name} due to organization creation error")
            else:
                print(
                    f"Found existing organization for {client_name}: {organization_id}")

            client_org_mapping[client_id] = organization_id

            # Fetch users for this client
            users = fetch_users_for_client(conn, client_id)

            # Add each user to the organization
            success_count = 0
            for user in users:
                user_id = user['id']
                username = user['username']
                password_hash = user['password_hash']

                # Fetch user roles from database
                user_roles = fetch_user_roles(conn, user_id)

                trusted_metadata = {
                    'user_id': str(user['id']),
                    'authorities': user_roles
                }
                # Add user to organization
                member_id = add_user_to_organization(
                    organization_id, username, trusted_metadata, password_hash)
                if member_id:
                    success_count += 1

            print(
                f"Added {success_count} out of {len(users)} users to organization {client_name}")

        print("\nMigration complete!")

    except Exception as e:
        print(f"An error occurred during migration: {e}")
    finally:
        conn.close()
        print("MySQL connection closed")


if __name__ == "__main__":
    main()
    # resp = stytch_client.passwords.authenticate(
    #     organization_id="organization-test-188179b3-3bb8-42b7-94d9-fea50c176d80",
    #     email_address="mgalindo@mangochango.com",
    #     password="rt-m#x9#",
    # )

    # print(resp)
