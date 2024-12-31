import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

app = Flask(__name__)
CORS(app)  # CORS 설정 추가

# Flask 서버 코드

@app.route('/')
def index():
    return "Heroku Flask App is running!"

@app.route('/transcript', methods=['POST'])
def get_transcript():
    # 디버깅용 로그 추가
    print("Request Headers:", request.headers)
    print("Request Body:", request.data)
    
    try:
        # 요청 데이터 확인
        data = request.json
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid request body. Expected JSON format."}), 400
        
        youtube_url = data.get("url")
        if not youtube_url:
            return jsonify({"error": "YouTube URL이 제공되지 않았습니다."}), 400
        
        # URL에서 비디오 ID 추출
        if "watch?v=" in youtube_url:
            video_id = youtube_url.split("watch?v=")[-1].split("&")[0]
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[-1].split("?")[0]
        else:
            return jsonify({"error": "유효하지 않은 YouTube URL입니다."}), 400

        # 자막 가져오기
        try:
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        except Exception as e:
            if "Subtitles are disabled" in str(e):
                return jsonify({"error": "자막이 비활성화된 동영상입니다."}), 400
            return jsonify({"error": str(e)}), 500

        priority_languages = ['ko', 'en']
        tran
