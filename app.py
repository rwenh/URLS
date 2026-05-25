import random
import string
from flask import Flask, request, jsonify, redirect, render_template, abort
from database import init_db, save_url, get_url, code_exists

app = Flask(__name__)
BASE_URL = "http://localhost:5000"
CODE_LENGTH = 6

def generate_code(length: int = CODE_LENGTH) -> str:
    """Generate a random alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if not code_exists(code):
            return code
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json(silent=True) or {}
    original_url = data.get("url", "").strip()

    if not original_url:
        return jsonify({"error": "url is required"}), 400
    # Basic URL validation
    if not original_url.startswith(("http://", "https://")):
        return jsonify({"error": "URL must start with http:// or https://"}), 400
    short_code = generate_code()
    save_url(short_code, original_url)

    return jsonify({
        "short_code": short_code,
        "short_url": f"{BASE_URL}/{short_code}",
        "original_url": original_url
    }), 201
@app.route("/<short_code>")
def redirect_to_url(short_code):
    original_url=get_url(short_code)
    if not original_url:
        abort(404)
    return redirect(original_url, code=302)
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Short URL not found"}), 404

@app.route("/favicon.ico")
def favicon():
    return "", 204

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
