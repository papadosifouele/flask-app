from flask import Flask, request, jsonify, render_template
import trimesh
import os
import requests  # Needed to send data to n8n

app = Flask(__name__)

UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Your n8n Webhook URL
N8N_WEBHOOK_URL = "https://eleftheria.app.n8n.cloud/webhook-test/file-upload"

@app.route('/')
def home():
    return render_template('index.html')  # Serves the HTML upload form

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        # Load the 3D model
        mesh = trimesh.load(file_path)

        # Check if the model has multiple layers (scenes)
        if isinstance(mesh, trimesh.Scene):
            lod_result = "IT IS LOD 200"
        else:
            lod_result = "IT IS LOD 100"

        # Extract 3D model properties
        bounding_box = mesh.bounding_box.extents.tolist() if hasattr(mesh, 'bounding_box') else []
        centroid = mesh.centroid.tolist() if hasattr(mesh, 'centroid') else []

        # Debug log (prints in Render logs)
        print(f"LOD Level: {lod_result}")
        print(f"Bounding Box: {bounding_box}")

        # Send JSON to n8n
        json_payload = {
            "message": "File processed successfully",
            "bounding_box": bounding_box,
            "centroid": centroid,
            "lod": lod_result  # This is what n8n needs
        }

        # Forward JSON to n8n Webhook
        response = requests.post(N8N_WEBHOOK_URL, json=json_payload)
        print(f"Sent to n8n: {response.status_code}")

        return jsonify(json_payload)  # Also return JSON to the user

    except Exception as e:
        print(f"Error processing file: {str(e)}")  # Log the error
        return jsonify({"error": str(e)}), 500

# Ensure the correct port for Render deployment
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
