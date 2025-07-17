#!/usr/bin/env python3
import yt_dlp
import sys

def test_simple_streaming():
    """Simple test of yt-dlp functionality"""
    video_id = "dQw4w9WgXcQ"
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    print(f"Testing yt-dlp with: {url}")
    
    try:
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extracting info...")
            info = ydl.extract_info(url, download=False)
            
            if info:
                print(f"✅ Success! Title: {info.get('title', 'Unknown')}")
                if 'url' in info:
                    print(f"✅ Stream URL found: {info['url'][:100]}...")
                    return True
                else:
                    print("❌ No direct URL in info")
                    formats = info.get('formats', [])
                    print(f"Found {len(formats)} formats")
                    if formats:
                        best = formats[0]
                        if 'url' in best:
                            print(f"✅ Format URL found: {best['url'][:100]}...")
                            return True
            else:
                print("❌ No info extracted")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_simple_streaming()
    sys.exit(0 if success else 1)