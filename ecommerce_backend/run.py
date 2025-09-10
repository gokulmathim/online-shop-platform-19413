from app import app
import os

def _get_host_port():
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    try:
        port = int(os.getenv("FLASK_RUN_PORT", "3001"))
    except ValueError:
        port = 3001
    return host, port

if __name__ == "__main__":
    """
    Entrypoint to run the Flask app.
    Respects env vars FLASK_RUN_HOST and FLASK_RUN_PORT (defaults 0.0.0.0:3001).
    """
    host, port = _get_host_port()
    app.run(host=host, port=port)
