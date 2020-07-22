from flaskapp import app, views, custom_config

port = custom_config.get('port', 5002)
host = custom_config.get('host', '127.0.0.1')


def main():
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
