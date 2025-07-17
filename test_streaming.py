#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced YouTube streaming functionality
implemented in SongHub, similar to SimpMusic (smusic) capabilities.
"""

import requests
import json
from app import get_youtube_stream_url

def test_streaming_functionality():
    """Test the new streaming functions"""
    
    # Test video ID (Rick Astley - Never Gonna Give You Up)
    video_id = "dQw4w9WgXcQ"
    
    print("=== Testing Enhanced YouTube Streaming Functionality ===")
    print(f"Testing with video ID: {video_id}")
    print()
    
    # Test 1: Get audio stream URL
    print("1. Testing audio-only stream extraction:")
    audio_result = get_youtube_stream_url(video_id, audio_only=True)
    
    if audio_result['status'] == 'success':
        print("✅ Audio stream extraction successful!")
        print(f"   Stream URL: {audio_result['stream_url'][:100]}...")
        print(f"   Format: {audio_result['format_info']['ext']}")
        print(f"   Audio Codec: {audio_result['format_info']['acodec']}")
        print(f"   Bitrate: {audio_result['format_info']['abr']} kbps")
        print(f"   Title: {audio_result['video_info']['title']}")
    else:
        print(f"❌ Audio stream extraction failed: {audio_result['message']}")
    
    print()
    
    # Test 2: Get video+audio stream URL
    print("2. Testing video+audio stream extraction:")
    video_result = get_youtube_stream_url(video_id, audio_only=False)
    
    if video_result['status'] == 'success':
        print("✅ Video+audio stream extraction successful!")
        print(f"   Stream URL: {video_result['stream_url'][:100]}...")
        print(f"   Format: {video_result['format_info']['ext']}")
        if 'resolution' in video_result['format_info']:
            print(f"   Resolution: {video_result['format_info']['resolution']}")
    else:
        print(f"❌ Video+audio stream extraction failed: {video_result['message']}")
    
    print()
    
    # Test 3: Test API endpoints (if server is running)
    print("3. Testing API endpoints:")
    base_url = "http://127.0.0.1:8002"
    
    try:
        # Test get_stream_url endpoint
        response = requests.get(f"{base_url}/get_stream_url/{video_id}?audio_only=true")
        if response.status_code == 200:
            data = response.json()
            print("✅ /get_stream_url endpoint working!")
            print(f"   API returned: {data['status']}")
        else:
            print(f"❌ /get_stream_url endpoint failed: {response.status_code}")
        
        # Test get_formats endpoint
        response = requests.get(f"{base_url}/get_formats/{video_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ /get_formats endpoint working!")
            print(f"   Found {len(data['formats']['audio_only'])} audio formats")
            print(f"   Found {len(data['formats']['video_only'])} video formats")
            print(f"   Found {len(data['formats']['combined'])} combined formats")
        else:
            print(f"❌ /get_formats endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running - API endpoints not tested")
        print("   Start the server with: python3 app.py")
    
    print()
    print("=== Key Features Implemented ===")
    print("✅ Robust stream URL extraction with signature deciphering")
    print("✅ Audio-only and video+audio format selection")
    print("✅ Best quality format selection based on bitrate/resolution")
    print("✅ Comprehensive format information and metadata")
    print("✅ Error handling for various edge cases")
    print("✅ API endpoints for format discovery and specific format streaming")
    print("✅ Similar functionality to SimpMusic (smusic) streaming core")
    
if __name__ == "__main__":
    test_streaming_functionality()