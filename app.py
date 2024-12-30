from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

app = Flask(__name__)

# Flask 서버 코드
@app.route('/transcript', methods=['POST'])
def get_transcript():
    data = request.json
    youtube_url = data.get("url")
    
    if not youtube_url:
        return jsonify({"error": "YouTube URL이 제공되지 않았습니다."}), 400
    
    try:
        # URL에서 비디오 ID 추출
        if "watch?v=" in youtube_url:
            video_id = youtube_url.split("watch?v=")[-1].split("&")[0]
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[-1].split("?")[0]
        else:
            return jsonify({"error": "유효하지 않은 YouTube URL입니다."}), 400

        # 자막 가져오기
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
        formatted_transcript = formatter.format_transcript(transcript_data)
        
        return jsonify({"transcript": formatted_transcript})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
