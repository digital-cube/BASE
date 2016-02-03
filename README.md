# **Base REST API** #

* Version 1.0
* [DigitalCube](http://digitalcube.rs/)

### Requirements ###

* Python3.5+
* [PIP](https://www.google.rs/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwjFx9KQwKHKAhUECCwKHVYBDDIQFggbMAA&url=https%3A%2F%2Fbootstrap.pypa.io%2Fget-pip.py&usg=AFQjCNE8Fo9j_sgo1hBzEoUT39H85hFDrg)
* build-essential
* mysql
* python3.5-dev
* libmysqlclient-dev


### Setup ###

    * pip3 install -r requirements.txt
    * make log dir:
         - mkdir /var/log/base (change permissions!!!)

### Use on Your project ###

    * open project beside BASE (BASE/mockupecho can be Your base template)

#### Settings ####
    * register Your application in BASE/config/settings.py APPS
    * configure Your api in Your project's \_\_init\_\_.py

### Start service ###
    cd api/install/dir/BASE

    python3 basemanager.py
    * or add link to /usr/local/bin
