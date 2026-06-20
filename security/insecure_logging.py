import logging

logging.basicConfig(level=logging.INFO)

def login(username, password):
    logging.info(
        f"Login attempt user={username} password={password}"
    )
