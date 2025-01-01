from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, CouldNotRetrieveTranscript
import logging
import os
import requests

app = Flask(__name__)

# Logger 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return jsonify({"message": "API is running!"})

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        # JSON 데이터 확인
        if not request.is_json:
            return jsonify({"error": "Invalid request format. Please send JSON."}), 400
        
        data = request.get_json()
        video_url = data.get("url")
        if not video_url:
            return jsonify({"error": "Missing 'url' in request body"}), 400

        # Video ID 추출
        try:
            if "watch?v=" in video_url:
                video_id = video_url.split("watch?v=")[-1].split("&")[0]
            elif "youtu.be/" in video_url:
                video_id = video_url.split("youtu.be/")[-1].split("?")[0]
            else:
                return jsonify({"error": "Invalid YouTube URL format."}), 400
            logger.info(f"Extracted video ID: {video_id}")
        except Exception as e:
            logger.error(f"Error extracting video ID: {e}")
            return jsonify({"error": "Unable to extract video ID."}), 400

        # 자막 가져오기
        try:
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
            priority_languages = ['ko', 'en']
            transcript = None

            for lang in priority_languages:
                try:
                    transcript = transcripts.find_transcript([lang])
                    break
                except Exception as e:
                    logger.warning(f"Transcript for language {lang} not found: {e}")
                    continue

            if transcript is None:
                try:
                    transcript = transcripts.find_generated_transcript(['ko', 'en'])
                except Exception as e:
                    logger.error(f"Generated transcript not found: {e}")
                    return jsonify({"error": "No transcript available for this video"}), 404

            transcript_data = transcript.fetch()
            full_text = " ".join([item['text'] for item in transcript_data])
            logger.info(f"Transcript successfully fetched for video ID {video_id}")
        except CouldNotRetrieveTranscript:
            logger.error(f"Transcript not available for video ID: {video_id}")
            return jsonify({"error": "Transcript not available for this video"}), 404
        except Exception as e:
            logger.error(f"Error fetching transcript: {e}")
            return jsonify({"error": "An error occurred while fetching the transcript."}), 500

        return jsonify({"transcript": full_text})

    except Exception as e:
        logger.error(f"Unexpected error in /summarize: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test_network', methods=['GET'])
def test_network():
    try:
        response = requests.get("https://www.youtube.com/")
        return jsonify({"status_code": response.status_code}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test_transcript', methods=['GET'])
def test_transcript():
    try:
        youtube_url = "https://www.youtube.com/watch?v=rzkXYXKWkvg"  # 테스트할 YouTube URL
        transcripts = YouTubeTranscriptApi.list_transcripts(youtube_url.split("v=")[-1])
        priority_languages = ['ko', 'en']
        transcript = None

        for lang in priority_languages:
            try:
                transcript = transcripts.find_transcript([lang])
                break
            except Exception as e:
                logger.warning(f"Transcript for language {lang} not found: {e}")
                continue

        if transcript is None:
            try:
                transcript = transcripts.find_generated_transcript(['ko', 'en'])
            except Exception as e:
                logger.error(f"Generated transcript not found: {e}")
                return jsonify({"error": "No transcript available for this video"}), 404

        transcript_data = transcript.fetch()
        full_text = " ".join([item['text'] for item in transcript_data])
        return jsonify({"transcript": full_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 로컬 테스트 시 실행
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
