from flask import Flask, request, jsonify, render_template
import trimesh
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')  # This serves the HTML file

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Extract 3D model properties
    mesh = trimesh.load(file_path)
    bounding_box = mesh.bounding_box.extents.tolist()
    centroid = mesh.centroid.tolist()

    return jsonify({
        "message": "File processed successfully",
        "bounding_box": bounding_box,
        "centroid": centroid
    })

if __name__ == '__main__':
    app.run(debug=True)
