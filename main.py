from flask import Flask, render_template, request, send_file, after_this_request
import os
from werkzeug.utils import secure_filename
from PIL import Image
import fitz  # PyMuPDF
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
CLEANED_FOLDER = "cleaned"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/strip", methods=["POST"])
def strip():
    file = request.files["file"]
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower()
    uid = str(uuid.uuid4())
    in_path = os.path.join(UPLOAD_FOLDER, uid + "_" + filename)
    out_path = os.path.join(CLEANED_FOLDER, "cleaned_" + filename)
    file.save(in_path)

    try:
        if ext == "pdf":
            doc = fitz.open(in_path)
            doc.set_metadata({})
            doc.save(out_path)
            doc.close()
        elif ext in ["jpg", "jpeg", "png", "gif", "webp", "bmp"]:
            img = Image.open(in_path)
            data = list(img.getdata())
            clean = Image.new(img.mode, img.size)
            clean.putdata(data)
            clean.save(out_path)
        else:
            return "Unsupported file type", 400
    except Exception as e:
        return f"Error processing file: {e}", 500

    # Clean up both input and output files after sending
    @after_this_request
    def cleanup(response):
        try:
            os.remove(in_path)
            os.remove(out_path)
        except Exception:
            pass
        return response

    return send_file(out_path, as_attachment=True)


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)