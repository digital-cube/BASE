## CHANGELOG

### 2019 08 26

## BASE version 1.12.1
- authorization decorator inject database session also

### 2019 08 25

## BASE version 1.12.0
- sqlalchemy database session is available through a request handler

### 2019 08 23

## BASE version 1.11.3
- fix for tests with postgresql

## BASE version 1.11.2
- fix for tests with postgresql

### 2019 08 21

## BASE version 1.11.0
- send mail over sendgrid
- forgot password will send email directly

## BASE version 1.10.2
- fix base handler and paths writer handler indexes

## BASE version 1.10.1
- fix type for authentication type WEAK
- handle bad secure cookie if authentication type is WEAK

### 2019 08 20

## BASE version 1.10.0
- api decorator accepts a list of URIs

### 2019 07 16

## BASE version 1.9.0
- API endpoints for tests only
- Tests helpers for dump/restore test databases user subprocess and wait for action

### 2019 03 15

## BASE version 1.8.16
- register user check roles bug fix
- tests with authentication_type COOKIE bug fix

### 2019 03 06

## BASE version 1.8.15
- week authentication bug fix

### 2019 03 05

## BASE version 1.8.14
- cookie authentication after social login

### 2019 03 05

## BASE version 1.8.13
- authentication token from bytes

### 2019 03 05

## BASE version 1.8.12
- authentication over cookie
- login and signup include secure cookie if configuration is present
- authentication can be week
- redirect url for not authenticated request

### 2019 01 25

## BASE version 1.8.11
- base return options updated

### 2019 01 24

## BASE version 1.8.10
- removed sqlalchemy session close for read instances

### 2019 01 21

## BASE version 1.8.9
- dump and restore databases in tests

### 2019 01 14

## BASE version 1.8.8
- service callbacks with app reference

### 2018 12 19

## BASE version 1.8.7
- register service callbacks

### 2018 12 10

## BASE version 1.8.6
- initialize sqlite database with alembic

### 2018 12 10

## BASE version 1.8.5
- initialize database with the existing alembic configuration and a new config file type

### 2018 12 10

## BASE version 1.8.4
- start read instances with the same executable as master

### 2018 11 29

## BASE version 1.8.3
- static uri from the configuration is added to all paths
- static path from the configuration is set as default static path

### 2018 11 28

## BASE version 1.8.2
- readonly decorator invalidates an database session

### 2018 11 28

## BASE version 1.8.1
- secure cookie as an authentication method

### 2018 10 22

## BASE version 1.8.0
- read only decorator 

### 2018 10 22

## BASE version 1.7.4
- default post_login_process hook with cookie setup
- default test class reset auth token on get_app

### 2018 10 12

## BASE version 1.7.3
- youtube link in posts
- tag manipulation

### 2018 10 03

## BASE version 1.7.2
- json API argument bug fix

### 2018 10 03

## BASE version 1.7.1
- import bug fix, files.py

### 2018 10 01

## BASE version 1.7.0
- new base component site - simple component contains page with url and meta part
- component builder improved
- blog component fixes
- post blog component has html meta field

### 2018 10 01

## BASE version 1.6.0
- param decorator's argument min and max works with string type
- param decorator's default argument handle changed - bug fix
- post statuses moved to the lookup file
- id for post mode changed to integer
- removed sequencer for post model
- post group presented, id_group (id of the post) and language is a uniqe combination
- post upgraded with a youtube link field
- tags (and show_tags) contains language, tag name and a language is a uniqu combination
- improved test for blog component
- timeout for test increased to 300s

### 2018 09 27

## BASE version 1.5.3
- language supported in url with __LANG__ url parameter
- language lookup

### 2018 09 21

## BASE version 1.5.2
- fix initialize database if models are already present

### 2018 09 20

## BASE version 1.5.1
- blog component improvement
- INSTALL.txt changed

### 2018 09 07

## BASE version 1.5.0
- the name of the package chagned to "dcbase"
- setup.py changed so the project can be uploaded to PYPI
- README.rst

### 2018 09 06

## BASE version 1.4.0
- database initialization if alembic structure is present, with new basemanager option
- API endpoints call counter
- specification template css correction

### 2018 09 03

## BASE version 1.3.0
- BASE component blog


### 2018 08 31

## BASE version 1.2.4
- project builder separated into maker module


### 2018 08 31

## BASE version 1.2.3
- facebook and google social login in tornado version > 5.0 process fix. Fix in tests for facebook social login.
- hooks for login and register accepts request handler as optional parameter


### 2018 08 28

## BASE version 1.2.2
- models configuration moved from the application config file to a separate json config file


### 2018 08 27

## BASE version 1.2.1
- db_init recognize configured application port if not in arguments


### 2018 08 27

## BASE version 1.2.0
- alembic as default database migration tool. Database are created with alembic. In tests sqlalchemy is used.


### 2018 07 30

## BASE version 1.1.6
- facebook social login included in the system


### 2018 07 27

## BASE version 1.1.5
- google social login included in the system


### 2018 07 06

## BASE version 1.1.4
- orm session as thread local session
- BASE version with separate numbers


### 2018 06 13

## BASE version 1.1.3
- base orm commit with session rollback on error or exception


### 2018 06 06

## BASE version 1.1.2
- prevent build project over existing models and files


### 2018 06 04

## BASE version 1.1.1
- pack user hook fix


### 2018 05 22

## BASE version 1.1.0
- pre application processes (configure in app_config)
- post application processes (configure in app_config)


### 2018 05 22

## BASE version 1.0.4
- data argument for the registration is not required anymore, and not saved to the database


### 2018 05 18

## BASE version 1.0.3
- new models Action and ActionSource presented
- new option in db_init - see db_init -h


### 2018 05 08

## BASE version 1.0.2
- default static file handler
- mockup api descriptions


### 2018 05 08

## BASE version 1.0.1

- remove parts of the system that are connected to database for initial instantiation,
and add them in database initialization process
- configure registration of allowed role flags
- move database destroy from teardown in tests to test's setup
- add project name to main template

### 2018 03 13

- strip and lower username for register user
- clear database for sqlite
- datetime.time as api parameter data type
- start base service without database configured (still as work in progress)

### 2018 01 21

- all sqlalchemy model files are with default charset

### 2018 01 19

- pre and post check user hooks

### 2017 12 12

- register user hook use User from AuthUser, not separate
- some commits are in tra/except with rollback (all commits should be with this)

### 2017 10 09

- change the way authentication decorator treat the roles provided in arguments. From now on roles can be provided as a list of arguments or as a logically combined role. For example @authentication(USER, ADMIN) or @authentication(USER | ADMIN).