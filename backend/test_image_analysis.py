#!/usr/bin/env python3
"""
Test script for image analysis functionality
"""
import asyncio
import httpx
import base64
import os

async def test_image_analysis():
    """Test the image analysis endpoints"""

    # Login to get token
    login_data = {
        "email_address": "admin@proteamcare.com.br",
        "password": "admin123"
    }

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Login
        print("🔐 Logging in...")
        response = await client.post("/api/v1/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return

        token_data = response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        print("✅ Login successful")

        # Test status endpoint
        print("📊 Testing status endpoint...")
        response = await client.get("/api/v1/image-analysis/status", headers=headers)
        print(f"Status response: {response.status_code} - {response.json()}")

        # Test with a simple base64 image (1x1 pixel PNG)
        print("🖼️ Testing base64 analysis...")
        # This is a minimal 1x1 transparent PNG in base64
        test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

        analysis_data = {
            "image_base64": test_image_b64,
            "mime_type": "image/png",
            "context": "test image for kanban board"
        }

        response = await client.post("/api/v1/image-analysis/analyze-base64",
                                   json=analysis_data, headers=headers)
        print(f"Analysis response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result}")
        else:
            print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_image_analysis())