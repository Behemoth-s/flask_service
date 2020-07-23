# 使用PyInstaller和Windows Service 发布Flask或Python项目

本文以Flask为例，介绍如何使用PyWin32将Python项目作为Windows Service运行，并使用PyInstaller将Python项目打包成二进制文件发布。

## Python环境

1. 创建虚拟环境

   ```shell
   conda create -n flask_service python=3.7
   ```

   使用虚拟环境可能会出现PyInstaller无法找到部分包的情况，如果不是很熟练，建议使用系统Python环境

2. 安装依赖

   ```shell
   pip install flask flask_restful pyinstaller pywin32
   ```

## 项目结构

文件目录如下

```c
+flask_service
│  flask_service.py    /* service启动 */
│  requirements.txt    /* dependencies */
│  run.py		       /* app启动 */
│  win_service.spec    /* PyInstaller配置 */
│
└─flaskapp             /* flask app */
   │  __init__.py
   │
   └─views             /* flask app 路由 */
      │  index.py
      └─ __init__.py

```

层级关系如下

```mermaid
graph TD;
    run.py--configure and run flask app-->flaskapp;
    flask_service.py--run as windows service-->run.py;
    PyInstaller--distribute service as exe-->flask_service.py;
```

首先需要创建一个`flask app`，使用`run.py`对`flask app`进行设置和调用，使用`flask_service.py`将python程序`run.py`封装成一个windows service服务，最后使用`PyInstaller`将服务打包成exe程序。

## Flask App

`Flask `项目设计可以参考[官方文档](https://flask.palletsprojects.com/en/1.1.x/tutorial/layout/)或者[典型案例](https://stackoverflow.com/a/37778716)。演示案例比较简单，只包含了`app`和`route`两部分，直接使用`flask_restful`来设置路由，存储在`view`目录下。

```
flaskapp
   │  __init__.py
   │
   └─views
      │  index.py
      └─ __init__.py
```

### flask app 初始化

```python
'''
flaskapp.__init__.py
'''

from flask import Flask
from flask_restful import Api
import logging

# set logger
logging.basicConfig(filename='C:\\Temp\\flask-service.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# create app
app = Flask(__name__)

# create api
api = Api(app)
```

### 路由

```python
'''
flaskapp.views.__init__.py
'''
from .index import Index

'''
flaskapp.views.index.py
'''

from flask_restful import Resource
from flaskapp import app, api

# create a rest Resource
class Index(Resource):
    def get(self):
        return 'hello world'

# add resource to route
api.add_resource(Index, '/')
```

需要注意的是，在案例的结构下，`from flaskapp import app`是不会加载路由的，必须先`from flaskapp import views`才会加载路由

### 启动Flask App

```python
'''
run.py
'''
# load app
from flaskapp import app
# load views
from flaskapp import views
# update config
app.config.update(**config_dict)
# run app
if __name__=="__main__":
	app.run(host='127.0.0.1', port='5001')
```

## Flask Service

使用`win32serviceutil.ServiceFramework`对`Flask App`进行封装，并实现`SvcStop`和`SvcDoRun`方法，实现方式如下

```python
'''
flask_service.py
'''
import win32serviceutil
import win32service
import win32event
import win32evtlogutil
import servicemanager
import socket
import time
import os
import sys

from run import app
import logging


class FlaskSvc(win32serviceutil.ServiceFramework):
    # service name
    _svc_name_ = "FlaskService"
    _svc_display_name_ = "Flask Service"

    def __init__(self, *args):
        win32serviceutil.ServiceFramework.__init__(self, *args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(5)
        self.stop_requested = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        logging.info('Stopped service ...')
        self.stop_requested = True

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        logging.info('start service ...')
        self.main()

    def main(self):
        app.run(host=app.config.get('host', '0.0.0.0'),
                port=app.config.get('port', 5008))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(FlaskSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(FlaskSvc)

```

### Service 使用

Windows Service需要管理员权限操作，启动Service之前需要安装Service

- 安装`Flask Service`

  ```shell
  python flask_service.py install
  ```

- 启动和停止`Flask Service`

  ```sehll
  python flask_service.py start
  python flask_service.py stop
  ```

- 调试

  ```shell
  python flask_service.py debug
  ```

- 卸载

  ```shell
  python flask_service.py remove
  ```

## Python Service的原理

Python Service的运行机理不同于一般的python程序，它并非运行在Python Interpreter之下，而是在加载之后由`PythonService.exe`执行。这种情况下主要有两个问题。由于无法插入断点，Debug运行时异常将会变得困难，需要借助日志进行排查。另一个是运行时路径和环境变量会发生变化，无法使用相对路径来定位，这点会在之后详细说明。

在执行`python flask_service.py install/debug/start`时，可能会发现PyCharm的Debugger似乎仍然是可以抓到断点，但是这并非真正的运行状态。在`flask_service.py`执行到最后一行`win32serviceutil.HandleCommandLine(FlaskSvc)`，它仍然是一个运行在Python Interpreter内的脚本，因此在此之前仍然是可以抓到断点的。

但是到了`win32serviceutil.HandleCommandLine`内，从源码来看则是通过Windows Service调用`PythonService.exe`执行。

- **CASE**: `start`

```python

'''
    cmd: python flask_service.py start
    source: win32serviceutil.py #599
    win32serviceutil.HandleCommandLine
'''
    if arg=="start":
        knownArg = 1
        print("Starting service %s" % (serviceName))
        try:
            StartService(serviceName, args[1:]) # serviceName:FlaskService, args[1:]: start
            if waitSecs:
                WaitForServiceStatus(serviceName, win32service.SERVICE_RUNNING, waitSecs)
        except win32service.error as exc:
            print("Error starting service: %s" % exc.strerror)
            err = exc.winerror
```

启动服务的命令为`StartService(serviceName, args[1:]) # serviceName:FlaskService, args[1:]: start`

因为，Service已经被安装，`start`在这里直接通过Windows Service Manager来启动服务。

`Flask Service`在Windows Service Manager内注册的程序正好是`PythonService.exe`，而`PythonService.exe`定位到项目路径则是通过注册表实现。

![image-20200723163152914](C:\Personal\project\flask_service\fig\image-20200723163152914.png)

- **CASE**:`debug`

```python
'''
    cmd: python flask_service.py debug
    source: win32serviceutil.py #617
    win32serviceutil.HandleCommandLine
'''
    elif arg=="debug":
        knownArg = 1
        if not hasattr(sys, "frozen"):
            # non-frozen services use pythonservice.exe which handles a
            # -debug option
            svcArgs = " ".join(args[1:])
            try:
                exeName = LocateSpecificServiceExe(serviceName)
            except win32api.error as exc:
                if exc.winerror == winerror.ERROR_FILE_NOT_FOUND:
                    print("The service does not appear to be installed.")
                    print("Please install the service before debugging it.")
                    sys.exit(1)
                raise
            try:
                # exeName:C:\\Personal\\MiniConda\\envs\\flask_service\\lib\\site-packages\\win32\\PythonService.exe
                os.system("%s -debug %s %s" % (exeName, serviceName, svcArgs))  # serviceName:FlaskService, svcArgs: debug
            # ^C is used to kill the debug service.  Sometimes Python also gets
            # interrupted - ignore it...
            except KeyboardInterrupt:
                pass
        else:
            # py2exe services don't use pythonservice - so we simulate
            # debugging here.
            DebugService(cls, args)
```

启动服务的命令为`os.system("%s -debug %s %s" % (exeName, serviceName, svcArgs))`由于ServiceManager不支持`debug`参数，所以这里直接通过命令行调用`PythonService.exe`传入了`debug`参数。

- **CASE**:`install`

1. 调用`win32serviceutil.InstallService`安装Service

   `serviceName:FlaskService`为服务名称

   `serviceClassString:C:\\Personal\\project\\flask_service\\flask_service.FlaskSvc`则指向了项目路径

```python
'''
    cmd: python flask_service.py install
    source: win32serviceutil.py #645
    win32serviceutil.HandleCommandLine
'''   
    if arg=="install":
        knownArg = 1
		'''
		*****ignore some code******
		'''
        try:
            # serviceClassString:C:\\Personal\\project\\flask_service\\flask_service.FlaskSvc
            InstallService(serviceClassString, serviceName, serviceDisplayName, serviceDeps = serviceDeps, startType=startup, bRunInteractive=interactive, userName=userName,password=password, exeName=exeName, perfMonIni=perfMonIni,perfMonDll=perfMonDll,exeArgs=exeArgs,
                           description=description, delayedstart=delayedstart)
            if customOptionHandler:

```

2. `win32service.CreateService`创建服务,并调用`InstallPythonClassString`

   `serviceName:FlaskService`为服务名称

   `commandLine:C:\\Personal\\MiniConda\\envs\\flask_service\\lib\\site-packages\\win32\\PythonService.exe`指向了服务运行路径

   向Windows Service Manager安装了服务

```python
                
'''
    cmd: python flask_service.py install
    source: win32serviceutil.py #134
    win32serviceutil.InstallService
'''                   
def InstallService(pythonClassString, serviceName, displayName, startType = None, errorControl = None, bRunInteractive = 0, serviceDeps = None, userName = None, password = None, exeName = None, perfMonIni = None, perfMonDll = None, exeArgs = None,
                   description = None, delayedstart = None):
'''
*************ignore some code************
'''
    hscm = win32service.OpenSCManager(None,None,win32service.SC_MANAGER_ALL_ACCESS)
    try:
        hs = win32service.CreateService(hscm,
                                serviceName,
                                displayName,
                                win32service.SERVICE_ALL_ACCESS,         # desired access
                    serviceType,        # service type
                    startType,
                    errorControl,       # error control type
                    commandLine,
                    None,
                    0,
                    serviceDeps,
                    userName,
                    password)
'''
************ignore some code***********
'''
    InstallPythonClassString(pythonClassString, serviceName)
    # If I have performance monitor info to install, do that.
    if perfMonIni is not None:
        InstallPerfmonForService(serviceName, perfMonIni, perfMonDll)

```

3. `win32service.InstallPythonClassString`绑定项目代码

   `pythonClassString:serviceClassString:C:\\Personal\\project\\flask_service\\flask_service.FlaskSvc`指向项目路径

   `serviceName:FlaskService`为服务名称

   通过注册表绑定了服务和项目代码

```python
'''
    cmd: python flask_service.py install
    source: win32serviceutil.py #252
    win32serviceutil.InstallPythonClassString
'''                   
def InstallPythonClassString(pythonClassString, serviceName):
    # Now setup our Python specific entries.
    if pythonClassString:
        key = win32api.RegCreateKey(win32con.HKEY_LOCAL_MACHINE, "System\\CurrentControlSet\\Services\\%s\\PythonClass" % serviceName)
        try:
            win32api.RegSetValue(key, None, win32con.REG_SZ, pythonClassString);
        finally:
            win32api.RegCloseKey(key)
```

## PyInstaller 发布

直接使用`PyInstaller`打包

```

```

