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

        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=3000,
            tlsCAFile=certifi.where()
        )

        await client.admin.command('ping')
        db = client[settings.DB_NAME]
        print("✅ Connected to MongoDB successfully")
        return db

    except Exception as e:
        print(f"⚠️  MongoDB skipped: {e}")
        print("⚠️  App works without database")
        return None


async def close_mongo_connection():
    global client
    if client:
        client.close()


def get_database():
    return db