# **Base REST API for DigitalCube projects** #

* Version 1.0
* [DigitalCube](http://digitalcube.rs/)

### Requirements ###

* Python3
* [PIP](https://www.google.rs/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwjFx9KQwKHKAhUECCwKHVYBDDIQFggbMAA&url=https%3A%2F%2Fbootstrap.pypa.io%2Fget-pip.py&usg=AFQjCNE8Fo9j_sgo1hBzEoUT39H85hFDrg)

### Setup ###

* pip3 install -r requirements.txt
* in .bash_profile (or .bashrc):
     - export PYTHONPATH="api/install/dir/digitalbaseapi:$PYTHONPATH"
* make log dir:
     - mkdir /var/log/digital (change permissions!!!)

### Use on Your project ###

* open project beside digitalbaseapi (digitalbaseapi/mockupecho can be Your base template)
* if You use pycharm (for Your project):
     - File -> Settings -> Project -> Project Structure:
        - Add Content Root (add digitalbaseapi dir)
        - select config and click on Source button, same for common dir
* #### Settings ####
    * register Your application in digitalbaseapi/config/settings.py APPS
    * configure Your api in Your project's \_\_init\_\_.py

### Start service ###
    cd api/install/dir/digitalbaseapi

    python3 service.py