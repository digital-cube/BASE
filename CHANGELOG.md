## CHANGELOG

### 2018 04 13

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