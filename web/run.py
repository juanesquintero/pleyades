from app import create_app

if __name__ == '__main__':
    #  Create application
    app = create_app()
    # Run server
    app.run(host='0.0.0.0', port=80)
