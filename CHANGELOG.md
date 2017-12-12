## CHANGELOG


### 2017 12 12

- register user hook user User from AuthUser, not separate
- some commits are in tra/except with rollback (all commits should be with this)

### 2017 10 09

- change the way authentication decorator treat the roles provided in arguments. From now on roles can be provided as a list of arguments or as a logically combined role. For example @authentication(USER, ADMIN) or @authentication(USER | ADMIN).