from flaskapp import app, views
import inspect
import os
import json

work_folder = os.path.dirname(inspect.currentframe().f_globals.get('__file__'))
app.logger.info('loading custom config from {}'.format(work_folder))
with open(os.path.join(work_folder, 'custom_config.json'), 'r') as fp:
    custom_config = json.load(fp)


def main():
    app.run(host='127.0.0.1', port=5001)


if __name__ == "__main__":
    main()
