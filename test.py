from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def extract_transcript_priority(youtube_url):
    try:
        if "watch?v=" in youtube_url:
            video_id = youtube_url.split("watch?v=")[-1].split("&")[0]
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[-1].split("?")[0]
        else:
            return "유효하지 않은 YouTube URL입니다."

        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        priority_languages = ['ko', 'en']
        transcript = None
        for lang in priority_languages:
            try:
                transcript = transcripts.find_transcript([lang])
                break
            except:
                continue

        if transcript is None:
            try:
                transcript = transcripts.find_generated_transcript()
            except:
                transcript = transcripts.find_transcript(transcripts._manually_created_transcripts.keys())

        transcript_data = transcript.fetch()
        formatter = TextFormatter()
        return formatter.format_transcript(transcript_data)

    except Exception as e:
        return f"에러가 발생했습니다: {e}"

youtube_url = "https://www.youtube.com/watch?v=lMU732cmG6w"
result = extract_transcript_priority(youtube_url)
print(result)
