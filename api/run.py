from app import create_app


app = create_app()

if __name__ == '__main__':
    # Run server
    app.run(host='0.0.0.0')
