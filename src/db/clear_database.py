from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

# MongoDB Atlas connection (HARD-CODED FOR DEMO ONLY)
MONGO_URL = "mongodb+srv://siddarthakoppaka:siddu42128@thinkwise-ai.a9l1iz2.mongodb.net/?retryWrites=true&w=majority&appName=thinkwise-ai"
DB_NAME = "rag_chat"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Connect to MongoDB
# Drop the entire database (This removes all collections and data)
client.drop_database(DB_NAME)

# Reconnect to fresh database
db = client[DB_NAME]

# Redefine collections
chat_sessions = db["chat_sessions"]
chat_history = db["chat_history"]

# Reinitialize the database indexes
def initialize_db():
    chat_sessions.create_index("session_id", unique=True)
    chat_history.create_index("session_id")

initialize_db()

print("Database reset successful!")
