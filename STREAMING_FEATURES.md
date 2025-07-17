# Enhanced YouTube Streaming Features

This document describes the enhanced YouTube streaming functionality implemented in SongHub, inspired by SimpMusic (smusic) streaming capabilities.

## Overview

The enhanced streaming system provides robust YouTube audio and video stream extraction with advanced format selection, signature deciphering, and comprehensive metadata retrieval.

## Key Features

### 1. Core Streaming Function

```python
get_youtube_stream_url(video_id, audio_only=True, preferred_quality='bestaudio')
```

**Features:**
- Automatic signature deciphering for protected streams
- Smart format selection based on quality preferences
- Comprehensive error handling
- Detailed metadata extraction
- Support for both audio-only and video+audio streams

### 2. API Endpoints

#### Get Stream URL
```
GET /get_stream_url/<video_id>?audio_only=true&quality=bestaudio
```

**Parameters:**
- `audio_only`: `true` for audio-only, `false` for video+audio (default: `true`)
- `quality`: `bestaudio`, `best`, or specific quality preference (default: `bestaudio`)

**Response:**
```json
{
  "status": "success",
  "stream_url": "https://...",
  "format_info": {
    "format_id": "140",
    "ext": "m4a",
    "acodec": "mp4a.40.2",
    "abr": 128,
    "asr": 44100,
    "filesize": 3456789,
    "quality": "medium"
  },
  "video_info": {
    "title": "Song Title",
    "duration": 180,
    "uploader": "Artist Name",
    "view_count": 1000000
  }
}
```

#### Get Available Formats
```
GET /get_formats/<video_id>
```

**Response:**
```json
{
  "status": "success",
  "video_info": {
    "title": "Song Title",
    "duration": 180,
    "uploader": "Artist Name",
    "view_count": 1000000,
    "description": "Video description..."
  },
  "formats": {
    "audio_only": [
      {
        "format_id": "140",
        "ext": "m4a",
        "acodec": "mp4a.40.2",
        "abr": 128,
        "asr": 44100,
        "url": "https://..."
      }
    ],
    "video_only": [
      {
        "format_id": "137",
        "ext": "mp4",
        "vcodec": "avc1.640028",
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "url": "https://..."
      }
    ],
    "combined": [
      {
        "format_id": "22",
        "ext": "mp4",
        "acodec": "mp4a.40.2",
        "vcodec": "avc1.64001F",
        "width": 1280,
        "height": 720,
        "url": "https://..."
      }
    ]
  },
  "recommended": {
    "best_audio": { /* best audio format */ },
    "best_video": { /* best video format */ },
    "best_combined": { /* best combined format */ }
  }
}
```

#### Get Specific Format Stream
```
GET /stream/<video_id>/<format_id>
```

**Response:**
```json
{
  "status": "success",
  "stream_url": "https://...",
  "format_info": {
    "format_id": "140",
    "ext": "m4a",
    "filesize": 3456789,
    "quality": "medium"
  }
}
```

## Implementation Details

### Signature Deciphering

The system automatically handles YouTube's signature cipher protection:

- Uses yt-dlp's built-in signature deciphering
- Supports both DASH and HLS manifests
- Handles encrypted stream URLs transparently

### Format Selection Algorithm

**Audio-only streams:**
1. Filter formats with audio codec and no video codec
2. Fallback to any format with audio if pure audio-only not available
3. Select best format based on audio bitrate (ABR) or total bitrate (TBR)

**Video+audio streams:**
1. Prefer combined formats with both audio and video
2. Select based on resolution and bitrate combination
3. Fallback to best available format

### Error Handling

- **Download errors**: Graceful handling of yt-dlp extraction failures
- **Format unavailability**: Automatic fallback to alternative formats
- **Network issues**: Proper error reporting with detailed messages
- **Invalid video IDs**: Clear error responses for non-existent videos

## Usage Examples

### Basic Audio Streaming

```python
# Get best audio stream
result = get_youtube_stream_url('dQw4w9WgXcQ', audio_only=True)
if result['status'] == 'success':
    audio_url = result['stream_url']
    print(f"Audio stream: {audio_url}")
```

### Advanced Format Selection

```python
# Get all available formats
response = requests.get('http://localhost:8002/get_formats/dQw4w9WgXcQ')
formats = response.json()

# Choose specific audio format
best_audio = formats['recommended']['best_audio']
format_id = best_audio['format_id']

# Get stream URL for specific format
stream_response = requests.get(f'http://localhost:8002/stream/dQw4w9WgXcQ/{format_id}')
stream_url = stream_response.json()['stream_url']
```

### Frontend Integration

```javascript
// Get audio stream for playback
async function playAudio(videoId) {
    const response = await fetch(`/get_stream_url/${videoId}?audio_only=true`);
    const data = await response.json();
    
    if (data.status === 'success') {
        const audio = new Audio(data.stream_url);
        audio.play();
    }
}

// Get format options for user selection
async function getFormatOptions(videoId) {
    const response = await fetch(`/get_formats/${videoId}`);
    const data = await response.json();
    
    return data.formats.audio_only.map(format => ({
        id: format.format_id,
        quality: `${format.abr || format.tbr}kbps ${format.ext}`,
        url: format.url
    }));
}
```

## Comparison with SimpMusic

This implementation provides similar functionality to SimpMusic (smusic):

✅ **Stream URL Extraction**: Direct access to YouTube audio/video streams
✅ **Signature Deciphering**: Automatic handling of encrypted URLs
✅ **Format Selection**: Smart quality-based format choosing
✅ **Metadata Extraction**: Comprehensive video information
✅ **Error Handling**: Robust error management
✅ **API Interface**: RESTful endpoints for integration

## Performance Considerations

- **Caching**: Consider implementing stream URL caching (URLs expire)
- **Rate Limiting**: YouTube may rate limit requests
- **Fallbacks**: Multiple format options ensure reliability
- **Async Processing**: Use async/await for better performance

## Security Notes

- Stream URLs are temporary and expire after some time
- No authentication required for public videos
- Respect YouTube's Terms of Service
- Consider implementing rate limiting for production use

## Testing

Run the test script to verify functionality:

```bash
python3 test_streaming.py
```

This will test:
- Audio stream extraction
- Video stream extraction
- API endpoint functionality
- Error handling

## Troubleshooting

**Common Issues:**

1. **"Requested format is not available"**
   - Try different quality settings
   - Check if video is available in your region
   - Use the `/get_formats` endpoint to see available options

2. **"No video information found"**
   - Verify the video ID is correct
   - Check if the video is public and accessible

3. **Stream URL expires quickly**
   - YouTube stream URLs are temporary
   - Re-fetch URLs when needed
   - Implement caching with appropriate TTL

4. **Rate limiting**
   - Implement delays between requests
   - Use connection pooling
   - Consider using multiple IP addresses for high-volume usage