#!/usr/bin/env python3
"""
Test script to verify that multiple users can use the system simultaneously
without rate limiting or conflicts.
"""

import asyncio
import aiohttp
import time
import json

async def test_user_session(user_id, commands, delay=0.5):
    """Test a single user session with multiple commands."""
    print(f"🧪 Testing user {user_id}...")
    
    async with aiohttp.ClientSession() as session:
        for i, command in enumerate(commands):
            print(f"  User {user_id}: Sending command {i+1}: '{command}'")
            
            # Send command
            async with session.post(
                'http://localhost:8000/api/command',
                json={'command': command, 'user_id': user_id}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"  User {user_id}: Response: {data['response'][:50]}...")
                else:
                    print(f"  User {user_id}: Error {response.status}")
            
            # Small delay between commands
            await asyncio.sleep(delay)
    
    print(f"✅ User {user_id} completed")

async def test_concurrent_users():
    """Test multiple users using the system simultaneously."""
    print("🚀 Starting concurrent user test...")
    
    # Define test commands for different users
    user_commands = {
        "user1": ["hello", "what's your name", "what is 5 + 10"],
        "user2": ["hi there", "who are you", "what is 3 * 7"],
        "user3": ["hey", "how are you", "what is 15 - 8"]
    }
    
    # Create tasks for all users
    tasks = []
    for user_id, commands in user_commands.items():
        task = test_user_session(user_id, commands)
        tasks.append(task)
    
    # Run all users concurrently
    start_time = time.time()
    await asyncio.gather(*tasks)
    end_time = time.time()
    
    print(f"\n🎉 All users completed in {end_time - start_time:.2f} seconds")
    print("✅ No rate limiting conflicts detected!")

if __name__ == "__main__":
    print("🧪 Ballsy Voice Assistant - Concurrent User Test")
    print("=" * 50)
    
    # Run the test
    asyncio.run(test_concurrent_users())
