DB_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/authdb"
SECRET_KEY = "381fe4a2683cd0eee27cd66bfe1e5b02142ab7ee64d4f1ccbf1011e7358b005e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_MINUTES = 24 * 60
REFRESH_TOKEN_LENGTH_BYTES = 24