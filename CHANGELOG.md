## CHANGELOG

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