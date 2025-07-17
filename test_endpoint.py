#!/usr/bin/env python3
import requests
import json

def test_streaming_endpoint():
    """Test the streaming endpoint directly"""
    base_url = "http://127.0.0.1:8002"
    video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    print("Testing streaming endpoint...")
    
    try:
        # Test audio-only streaming
        print("\n1. Testing audio-only streaming:")
        response = requests.get(f"{base_url}/get_stream_url/{video_id}?audio_only=true", timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get('status') == 'success':
                print("✅ Audio streaming working!")
                stream_url = data.get('stream_url')
                if stream_url:
                    print(f"Stream URL: {stream_url[:100]}...")
                else:
                    print("❌ No stream URL in response")
            else:
                print(f"❌ Error in response: {data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on port 8002?")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    try:
        # Test format discovery
        print("\n2. Testing format discovery:")
        response = requests.get(f"{base_url}/get_formats/{video_id}", timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                audio_count = len(data.get('audio_formats', []))
                video_count = len(data.get('video_formats', []))
                combined_count = len(data.get('combined_formats', []))
                print(f"✅ Found {audio_count} audio, {video_count} video, {combined_count} combined formats")
            else:
                print(f"❌ Error: {data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server for format discovery")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_streaming_endpoint()