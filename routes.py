import os, logging
from flask import jsonify, request, Response
from pathlib import Path
from services.wav2lip_inference import run_wav2lip_inference
from utils import get_uploads_dir
from werkzeug.utils import secure_filename




DEFAULT_AUDIO_FILENAME = "audio.webm"
DEFAULT_VIDEO_FILENAME = "face.webm"
DEFAULT_OUTPUT_FILENAME = "output.mp4"



def init_app(app):
    @app.route("/uploads/<filename>", methods=["GET"])
    def uploaded_file(filename):
        
        filename = secure_filename(filename)
        uploads_dir = get_uploads_dir()
        fullpath = os.path.normpath(os.path.join(uploads_dir, filename))
    
        if not fullpath.startswith(uploads_dir):
            return jsonify(error="Access denied"), 403
        
        try:
            with open(fullpath, "rb") as f:
                file_content = f.read()
            return Response(file_content, content_type="video/webm")
        except FileNotFoundError:
            return jsonify(error="File not found"), 404

    


    @app.route("/api/files", methods=["POST"])
    def files():
        print("request files",request.files)
        if "audio" not in request.files or "video" not in request.files:
            return jsonify(error="Missing audio or video file"), 400
        
        print("files",request.files)
        
        audio_file = request.files["audio"]
        video_file = request.files["video"]


        try:
            audio_save_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static", audio_file.filename)
            print("audio File path:", audio_save_path)
            audio_file.save(audio_save_path)
            video_save_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static", video_file.filename)
            file = os.path.splitext(video_save_path)[0]
            audio_file.save(video_save_path)
            print("video File path:", video_save_path)
            output_path = os.path.join(get_uploads_dir(),"outputs" ,file+"_"+DEFAULT_OUTPUT_FILENAME)
            print("output File path:", output_path)
            try:
                run_wav2lip_inference(
                face_path=video_save_path, audio_path=audio_save_path, outfile_path=output_path
                )
                print("output File path:", output_path)
            except Exception as e:
                # raise Exception("Error: " + str(e))
                print("Error: " + str(e))
            if Path(output_path).is_file():
                    return (
                        jsonify(videoPath=output_path),
                        200,
                    )
            else:
                    return (
                        jsonify(error="Output file not found."),
                        404,
                    )



        except Exception as e:
            # raise Exception("Error in saving file: " + str(e))
            print("Error in saving file:",e)

       
       


