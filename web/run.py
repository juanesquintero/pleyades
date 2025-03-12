import argparse
from flask import Flask
from app import create_app, create_celery_app


def start_flask_app(app: Flask):
    """Start the Flask application."""
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)


def start_celery_worker(app: Flask):
    """Start the Celery worker."""
    celery = create_celery_app(app)
    print("Starting Celery worker...")
    celery.worker_main(argv=['worker', '--loglevel=info'])


if __name__ == '__main__':
    # Create a single Flask app instance
    app = create_app()

    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Run the Flask application and Celery worker."
    )
    parser.add_argument(
        "--celery",
        "-c",
        action="store_true",
        help="Run as a Celery worker"
    )

    args = parser.parse_args()

    # Determine what to run based on the --celery flag
    if args.celery:
        start_celery_worker(app)
    else:
        start_flask_app(app)
