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

    # Load the 3D model
    mesh = trimesh.load(file_path)

    # Check if the model has layers
    has_layers = hasattr(mesh, 'metadata') and 'layers' in mesh.metadata and mesh.metadata['layers']

    # Determine LOD
    lod_result = "IT IS LOD 200" if has_layers else "IT IS LOD 100"

    # Extract 3D model properties
    bounding_box = mesh.bounding_box.extents.tolist()
    centroid = mesh.centroid.tolist()

    return jsonify({
        "message": "File processed successfully",
        "bounding_box": bounding_box,
        "centroid": centroid,
        "lod": lod_result  # Send LOD status
    })

if __name__ == '__main__':
    app.run(debug=True)
