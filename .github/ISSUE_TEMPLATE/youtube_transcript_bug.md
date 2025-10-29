---
name: YouTube Transcript Extraction Failing
about: YouTube transcript extraction returns "no element found" error
title: '[BUG] YouTube transcript extraction fails with XML parsing error'
labels: bug, enhancement, streamlit
assignees: ''
---

## Bug Description

YouTube transcript extraction feature in Streamlit app fails with error:
```
❌ Error: no element found: line 1, column 0
```

## To Reproduce

**Steps:**
1. Open Streamlit app: `streamlit run lumibot_strategy_generator_enhanced.py`
2. Select "YouTube URL" input method
3. Enter YouTube URL: https://www.youtube.com/watch?v=vGU5br1papc
4. Click "📺 Extract Transcript"
5. Error appears

**Expected Behavior:**
- Should extract video transcript
- Store in session state
- Display success message with character count

**Actual Behavior:**
- XML parsing error: "no element found: line 1, column 0"
- No transcript extracted

## Environment

- **OS:** Windows 11
- **Python:** 3.13.3
- **Streamlit:** (check version)
- **youtube-transcript-api:** (check version)
- **Branch:** feature/two-stage-workflow-playwright

## Root Cause Analysis

### Possible Causes

1. **Video has no captions/transcript**
   - Not all YouTube videos have captions enabled
   - Some creators disable automatic captions
   - API can't extract what doesn't exist

2. **YouTube API restrictions**
   - YouTube may block automated transcript requests
   - Rate limiting on transcript API
   - API access restrictions for certain videos

3. **Library compatibility**
   - youtube-transcript-api may need updating
   - Breaking changes in YouTube's internal API
   - XML response format changed

4. **Network/firewall issues**
   - Corporate firewall blocking YouTube API
   - VPN interference
   - Regional restrictions

## Investigation Steps

### 1. Check Video Has Captions
```bash
# Manually verify video has CC button in YouTube player
# Test with known-good video that definitely has captions
```

### 2. Check Library Version
```bash
pip show youtube-transcript-api
# Update to latest if outdated
pip install --upgrade youtube-transcript-api
```

### 3. Test with Different Videos
Try these known-good videos with captions:
- Educational channels (usually have captions)
- TED Talks (always captioned)
- Official trading education channels

### 4. Add Debug Logging
```python
# In lumibot_strategy_generator_enhanced.py
import logging
logging.basicConfig(level=logging.DEBUG)

try:
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    logging.debug(f"Transcript fetched: {len(transcript_list)} segments")
except Exception as e:
    logging.error(f"Full error: {e.__class__.__name__}: {str(e)}")
    logging.error(f"Video ID: {video_id}")
```

## Workarounds

### Current Workaround: Use Text Input
1. Select "Text Input" method instead
2. Manually copy/paste video description or notes
3. Generate instruction file from text

### Alternative: Manual Transcript Download
1. Open YouTube video
2. Click "..." → "Show transcript"
3. Copy transcript text
4. Paste into "Text Input" in Streamlit app

### Future Enhancement: Add Fallback
```python
# Try multiple transcript languages
for lang in ['en', 'en-US', 'en-GB']:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        break
    except:
        continue
```

## Proposed Solutions

### Short-term (Quick Fix)
- [ ] Add better error message explaining the issue
- [ ] Suggest Text Input as alternative
- [ ] Add "Copy transcript from YouTube manually" instructions
- [ ] Validate video has captions before attempting extraction

### Medium-term (Enhanced UX)
- [ ] Update `youtube-transcript-api` to latest version
- [ ] Add retry logic with exponential backoff
- [ ] Try multiple language codes
- [ ] Detect if video has captions available before extraction
- [ ] Show helpful error messages based on error type

### Long-term (Alternative Approach)
- [ ] Consider alternative transcript extraction methods
- [ ] Add support for manual transcript paste
- [ ] Integrate with YouTube Data API v3 for caption availability check
- [ ] Add option to upload .srt/.vtt caption files directly

## Priority

**Medium Priority**
- Feature currently has workaround (Text Input)
- Not blocking core functionality
- Affects user experience but not critical path
- Two-stage workflow works fine with Text Input

## Labels

- `bug` - Current implementation fails
- `enhancement` - Needs improved error handling
- `streamlit` - Affects Streamlit UI
- `good-first-issue` - Clear scope, good for contributors

## Related Issues

- None yet

## Additional Context

This issue was discovered during testing of the two-stage workflow refactoring (feature/two-stage-workflow-playwright branch). The Text Input and PDF Upload methods work correctly - only YouTube transcript extraction is affected.

**Testing Note:**
Focus testing on Text Input method until YouTube issue is resolved. The core workflow (instruction file generation → /lumibot-generate → strategy code) works regardless of input method.
