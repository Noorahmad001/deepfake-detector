import motor.motor_asyncio
import certifi
from app.config.settings import settings

client = None
db = None

async def connect_to_mongo():
    global client, db
    try:
        if not settings.MONGODB_URL:
            print("⚠️  No MongoDB URL found")
            return None

        print(f"🔌 Connecting to MongoDB...")
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            tlsCAFile=certifi.where(),
            retryWrites=True,
            w="majority"
        )

        # Test connection with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await client.admin.command('ping')
                db = client[settings.DB_NAME]
                print("✅ Connected to MongoDB successfully")
                return db
            except Exception as ping_error:
                if attempt < max_retries - 1:
                    print(f"⚠️  MongoDB ping failed (attempt {attempt + 1}/{max_retries}): {ping_error}")
                    print("⚠️  Retrying in 2 seconds...")
                    import asyncio
                    await asyncio.sleep(2)
                else:
                    raise ping_error

    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        print("⚠️  App works without database")
        return None


async def close_mongo_connection():
    global client
    if client:
        client.close()


def get_database():
    return db