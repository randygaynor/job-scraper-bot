import os
from flask import Flask, send_file, abort, render_template_string
from job_scraper_bot.config import WEB_HOST, WEB_PORT, DIGEST_HTML_FILE, resolve_path

app = Flask(__name__)
DIGEST_PATH = resolve_path(DIGEST_HTML_FILE)


@app.route("/")
def homepage():
    if os.path.exists(DIGEST_PATH):
        return send_file(DIGEST_PATH)
    return render_template_string(
        "<html><body><h1>No job digest available yet</h1><p>Run the scraper first to generate an output digest.</p></body></html>"
    )


@app.route("/refresh")
def refresh():
    if os.path.exists(DIGEST_PATH):
        return send_file(DIGEST_PATH)
    abort(404)


@app.route("/health")
def health():
    return {"status": "ok"}


def run_app():
    app.run(host=WEB_HOST, port=WEB_PORT, debug=False)


if __name__ == "__main__":
    run_app()
