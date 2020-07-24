from flaskapp import app, views
import inspect
import os
import sys
import json

# port = custom_config.get('port', 5002)
# host = custom_config.get('host', '127.0.0.1')

app.logger.info('relative_path:{}'.format(os.path.abspath('.')))

app.logger.info(
    'inspect path:{}'.format(
        os.path.dirname(inspect.currentframe().f_globals.get('__file__'))))
app.logger.info('_MEIPASS env:{}'.format(os.environ.get("_MEIPASS2", 'None')))
try:
    pyinstaller_path = sys._MEIPASS
except:
    pyinstaller_path = os.environ.get("_MEIPASS2", 'None')
app.logger.info('pyinstaller path:{}'.format(pyinstaller_path))

# load custom config
# def resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and for PyInstaller """
#     try:
#         # PyInstaller creates a temp folder and stores path in _MEIPASS
#         base_path = sys._MEIPASS
#         app.logger.info(base_path)
#         app.logger.info(os.path.abspath('.'))
#     except Exception:
#         base_path = os.environ.get("_MEIPASS2", os.path.abspath("."))
#     return os.path.join(base_path, relative_path)
#
#
# custom_config_file = resource_path('custom_config.json')
# if os.path.isfile(custom_config_file):
#     app.logger.info(
#         'load custom config from file {}'.format(custom_config_file))
#     custom_config = json.load(open(resource_path('custom_config.json')))
# else:
#     app.logger.error(
#         'custom config file {} not found'.format(custom_config_file))
#     import inspect
#
#     path = inspect.currentframe().f_globals.get('__path__')
#     app.logger.info('inspect path {}'.format(path))
#     app.logger.info('sys argv {}'.format(str(sys.argv)))
#
#     app.logger.info('sys excutable {}'.format(str(sys.executable)))
#     app.logger.info('sys keys {}'.format(str(sys.__dict__.keys())))
#     custom_config = {}

custom_config = {}


def main():
    app.run(host='127.0.0.1', port=5001)


if __name__ == "__main__":
    main()
