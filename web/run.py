import debugpy
import argparse
from app import create_app, create_celery_app


def start_flask_app():
    ### Start the Flask application.###
    app = create_app()
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=80, debug=True)
    return app


def start_celery_worker():
    ### Start the Celery worker.###
    app = start_flask_app()
    celery = create_celery_app(app)
    print("Starting Celery worker...")
    celery.worker_main(argv=['worker', '--loglevel=info'])


if __name__ == '__main__':
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Run the application in different modes."
    )
    parser.add_argument(
        "celery",
        action="store_true",
        help="Run as a Celery worker"
    )

    args = parser.parse_args()

    # Determine what to run based on the --celery flag
    if args.celery:
        start_celery_worker()
    else:
        start_flask_app()
