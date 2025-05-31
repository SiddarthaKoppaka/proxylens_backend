from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

# MongoDB Atlas connection (HARD-CODED FOR DEMO ONLY)
MONGO_URL = "mongodb+srv://siddarthakoppaka:siddu42128@thinkwise-ai.a9l1iz2.mongodb.net/?retryWrites=true&w=majority&appName=thinkwise-ai"
DB_NAME = "rag_chat"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
chat_sessions = db["chat_sessions"]
chat_history = db["chat_history"]

# Define collection
chat_sessions = db["chat_sessions"]

def initialize_db():
    """Ensures necessary MongoDB indexes exist."""
    chat_sessions.create_index("session_id", unique=True)
    print("[INFO] Database initialized with indexes.")

def add_message(session_id, user_query, bot_response):
    """
    Stores a new message in chat history under the corresponding session.
    If the session doesn't exist, it creates a new one.
    """
    session = chat_sessions.find_one({"session_id": session_id})

    chat_entry = {
        "user": user_query,
        "bot": bot_response,
        "timestamp": datetime.utcnow()
    }

    if session:
        # Append new message to existing session
        result = chat_sessions.update_one(
            {"session_id": session_id},
            {"$push": {"chats": chat_entry}}
        )
        if result.modified_count > 0:
            print(f"[SUCCESS] Added message to existing session: {session_id}")
        else:
            print(f"[WARNING] Message not added to session: {session_id}")
    else:
        # Create a new session with first message
        chat_sessions.insert_one({
            "session_id": session_id,
            "title": user_query,  # Use the first user query as the title
            "chats": [chat_entry]
        })
        print(f"[SUCCESS] New session created: {session_id}")

def get_chat_history(session_id, limit=5):
    """
    Retrieves the latest 'limit' chat messages for a session.
    """
    session = chat_sessions.find_one({"session_id": session_id}, {"_id": 0, "chats": 1})
    
    if session and "chats" in session:
        print(f"[INFO] Retrieved {len(session['chats'][-limit:])} messages from session: {session_id}")
        return session["chats"][-limit:]  # Return last 'limit' messages
    
    print(f"[WARNING] No chat history found for session: {session_id}")
    return []

def clear_chat_history(session_id):
    """
    Deletes a session and its chat history.
    """
    result = chat_sessions.delete_one({"session_id": session_id})
    
    if result.deleted_count > 0:
        print(f"[SUCCESS] Cleared chat history for session: {session_id}")
    else:
        print(f"[WARNING] No session found to delete: {session_id}")

def get_all_chat_sessions():
    """
    Retrieves all chat session IDs and titles from MongoDB.
    """
    sessions = chat_sessions.find({}, {"_id": 0, "session_id": 1, "title": 1, "chats": 1})
    session_list = []

    for session in sessions:
        session_data = {
            "session_id": session["session_id"], 
            "title": session.get("title", "Untitled Chat"),
            "last_updated": session["chats"][-1]["timestamp"] if session.get("chats") else None
        }
        session_list.append(session_data)

    print(f"[INFO] Retrieved {len(session_list)} chat sessions.")
    return session_list

# Initialize MongoDB collections and indexes
initialize_db()
