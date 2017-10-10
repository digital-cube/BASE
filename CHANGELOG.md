## CHANGELOG

### 2017 10 09

- change the way authentication decorator treat the roles provided in arguments. From now on roles can be provided as a list of arguments or as a logically combined role. For example @authentication(USER, ADMIN) or @authentication(USER | ADMIN).