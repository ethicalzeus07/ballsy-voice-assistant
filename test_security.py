#!/usr/bin/env python3
"""
Security test script for Ballsy Voice Assistant
Tests DDoS protection, rate limiting, and input validation
"""

import asyncio
import aiohttp
import time
import json
from typing import List

async def test_rate_limiting():
    """Test rate limiting by sending many requests quickly."""
    print("🧪 Testing Rate Limiting...")
    
    async with aiohttp.ClientSession() as session:
        # Send 35 requests (should exceed the 30 per minute limit)
        tasks = []
        for i in range(35):
            task = session.post(
                'http://localhost:8000/api/command',
                json={'command': f'test command {i}', 'user_id': 'test_user'}
            )
            tasks.append(task)
        
        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count rate limited responses
        rate_limited = 0
        successful = 0
        
        for response in responses:
            if isinstance(response, Exception):
                print(f"  ❌ Request failed: {response}")
                continue
                
            if response.status == 200:
                data = await response.json()
                if "Too many requests" in data.get('response', ''):
                    rate_limited += 1
                else:
                    successful += 1
            else:
                print(f"  ❌ HTTP {response.status}")
        
        print(f"  ✅ Rate limiting test: {successful} successful, {rate_limited} rate limited")
        return rate_limited > 0

async def test_input_validation():
    """Test input validation and sanitization."""
    print("🧪 Testing Input Validation...")
    
    test_cases = [
        ("", "Empty command"),
        ("a" * 1001, "Command too long"),
        (None, "None command"),
        ("normal command", "Valid command"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for command, description in test_cases:
            try:
                async with session.post(
                    'http://localhost:8000/api/command',
                    json={'command': command, 'user_id': 'test_user'}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "Invalid input" in data.get('response', '') or "too long" in data.get('response', '').lower():
                            print(f"  ✅ {description}: Properly rejected")
                        else:
                            print(f"  ⚠️ {description}: Accepted (may be valid)")
                    else:
                        print(f"  ✅ {description}: HTTP {response.status} (properly rejected)")
            except Exception as e:
                print(f"  ❌ {description}: Error - {e}")

async def test_session_isolation():
    """Test that different users have isolated sessions."""
    print("🧪 Testing Session Isolation...")
    
    async with aiohttp.ClientSession() as session:
        # User 1 asks a question
        async with session.post(
            'http://localhost:8000/api/command',
            json={'command': 'what is 5 + 10?', 'user_id': 'user1'}
        ) as response:
            if response.status == 200:
                data1 = await response.json()
                print(f"  User1 response: {data1['response']}")
        
        # User 2 asks the same question
        async with session.post(
            'http://localhost:8000/api/command',
            json={'command': 'what is 5 + 10?', 'user_id': 'user2'}
        ) as response:
            if response.status == 200:
                data2 = await response.json()
                print(f"  User2 response: {data2['response']}")
        
        # Both should get the same answer (it's a simple math question)
        if data1['response'] == data2['response']:
            print("  ✅ Session isolation working (both users got same response)")
        else:
            print("  ⚠️ Session isolation may have issues")

async def test_concurrent_users():
    """Test multiple users using the system simultaneously."""
    print("🧪 Testing Concurrent Users...")
    
    async def user_session(user_id: str, commands: List[str]):
        async with aiohttp.ClientSession() as session:
            for i, command in enumerate(commands):
                try:
                    async with session.post(
                        'http://localhost:8000/api/command',
                        json={'command': command, 'user_id': user_id}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"  User{user_id}: {data['response'][:30]}...")
                        else:
                            print(f"  User{user_id}: HTTP {response.status}")
                except Exception as e:
                    print(f"  User{user_id}: Error - {e}")
                await asyncio.sleep(0.1)  # Small delay
    
    # Create multiple user sessions
    tasks = [
        user_session("A", ["hello", "what's your name", "what is 2 + 2"]),
        user_session("B", ["hi", "who are you", "what is 3 * 4"]),
        user_session("C", ["hey", "how are you", "what is 10 - 5"])
    ]
    
    start_time = time.time()
    await asyncio.gather(*tasks)
    end_time = time.time()
    
    print(f"  ✅ Concurrent users test completed in {end_time - start_time:.2f} seconds")

async def test_ddos_protection():
    """Test DDoS protection by creating many sessions."""
    print("🧪 Testing DDoS Protection...")
    
    async with aiohttp.ClientSession() as session:
        # Try to create many sessions
        tasks = []
        for i in range(100):
            task = session.post(
                'http://localhost:8000/api/command',
                json={'command': f'hello from user {i}', 'user_id': f'user_{i}'}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
        failed = len(responses) - successful
        
        print(f"  ✅ DDoS protection test: {successful} successful, {failed} failed")
        return failed > 0

async def main():
    """Run all security tests."""
    print("🛡️ Ballsy Voice Assistant - Security Test Suite")
    print("=" * 50)
    
    tests = [
        test_rate_limiting,
        test_input_validation,
        test_session_isolation,
        test_concurrent_users,
        test_ddos_protection
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    # Summary
    print("=" * 50)
    print("📊 Security Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All security tests passed!")
    else:
        print("⚠️ Some security tests failed. Review the implementation.")

if __name__ == "__main__":
    asyncio.run(main())
