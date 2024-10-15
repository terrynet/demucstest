from flask import Flask, request, send_file
import os
from pathlib import Path
import demucs.separate
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

# Ensure the upload and processed directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


def run_demucs(track_name, model="htdemucs_6s", device="cpu", shifts=1, overlap=0.25, filename="{track}_{stem}.wav"):
    """
    Run Demucs separation on the given audio track.
    """
    args = [
        track_name,  # Path to the audio file
        "-n", model,  # Model name (e.g., htdemucs_6s)
        "-d", device,  # Device (e.g., "cpu" or "cuda")
        "--shifts", str(shifts),  # Number of shifts
        "--overlap", str(overlap),  # Overlap between chunks
        "--filename", filename,  # Custom filename template
    ]
    
    # Call the Demucs separator
    demucs.separate.main(args)


@app.route('/upload', methods=['POST'])
def upload_audio():
    """
    Endpoint to upload an audio file. It will process the file with Demucs
    and return the separated stems as a zip file.
    """
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']

    if file.filename == '':
        return "No selected file", 400

    if file:
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Process the file with Demucs
        output_dir = os.path.join(PROCESSED_FOLDER, Path(file.filename).stem)
        os.makedirs(output_dir, exist_ok=True)
        
        # Run the Demucs separation
        run_demucs(track_name=file_path)

        # Remove the original MP3 file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

        # Return the processed stems as a zip file
        zip_filename = f"{Path(file.filename).stem}_stems.zip"
        zip_filepath = os.path.join(PROCESSED_FOLDER, zip_filename)

        with shutil.ZipFile(zip_filepath, 'w') as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_dir))

        return send_file(zip_filepath, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=True)
