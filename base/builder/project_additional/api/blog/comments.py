# coding= utf-8

from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated

from src.common.common import add_comment
from src.common.common import get_comments


@api(
    URI='/wiki/posts/:id_post/authorized/comments'
)
@authenticated()
class AuthorizedComment(Base):

    @params(
        {'name': 'id_post', 'type': str, 'doc': 'id', 'required': True},
        {'name': 'text', 'type': str, 'doc': 'comment', 'required': False},
        {'name': 'id_parent_comment', 'type': int, 'doc': 'id_parent_comment', 'required': False},
    )
    def put(self, id_post, text, id_parent_comment):
        return add_comment(id_post, text, id_parent_comment, self.auth_user.user, None, None, self)


@api(
    URI='/wiki/posts/:id_post/comments'
)
class UnauthorizedComment(Base):

    @params(
        {'name': 'id_post', 'type': str, 'doc': 'id', 'required': True},
        {'name': 'text', 'type': str, 'doc': 'comment', 'required': False},
        {'name': 'email', 'type': 'email', 'doc': 'email', 'required': False},
        {'name': 'display_name', 'type': 'str', 'doc': 'email', 'required': False},
        {'name': 'id_parent_comment', 'type': int, 'doc': 'id_parent_comment', 'required': False},
    )
    def put(self, id_post, text, email, display_name, id_parent_comment):
        return add_comment(id_post, text, id_parent_comment, None, email.lower() if email else None, display_name, self)

    @params(
        {'name': 'id_post', 'type': str, 'doc': 'id', 'required': True},
        {'name': 'canonical', 'type': bool, 'doc': 'canonical', 'requested': False, 'default': False}
    )
    def get(self, id_post, canonical):
        successfull, res = get_comments(id_post, canonical)

        if not successfull:
            return self.error(res)

        return self.ok({'comments': res})


