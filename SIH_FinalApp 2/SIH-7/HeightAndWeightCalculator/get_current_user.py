#!/usr/bin/env python3
"""
Helper script to get current logged-in user from Flask session
"""

import os
import sys
from pymongo import MongoClient
from bson import ObjectId

def get_current_user_email():
    """Get current user email from Flask session or MongoDB"""
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['sih2573']
        users = db['users']
        
        # For now, get the most recent user (you can modify this logic)
        # In a real app, this would come from Flask session
        user = users.find_one(sort=[('created_at', -1)])
        
        if user:
            return user.get('email')
        
        return None
        
    except Exception as e:
        print(f"Error getting current user: {e}")
        return None

if __name__ == "__main__":
    email = get_current_user_email()
    if email:
        print(email)
    else:
        print("No user found")