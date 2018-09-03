# coding= utf-8

import json
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated

import datetime
from src.models.knowledgebase import Post, Tag
from src.common.common import get_comments
from src.common.common import get_post_files


@authenticated()
@api(
    URI='/wiki/posts'
)
class AddPost(Base):

    @params(  # if you want to add params
        {'name': 'title', 'type': str, 'doc': 'title', 'required': True},
        {'name': 'subtitle', 'type': str, 'doc': 'subtitle', 'required': False},
        {'name': 'body', 'type': json, 'doc': 'body', 'required': True},
        {'name': 'category', 'type': str, 'doc': 'category', 'required': False},
        {'name': 'tags', 'type': list, 'doc': 'list of tags', 'required': False},
        {'name': 'slug', 'type': str, 'doc': 'slug', 'required': False},
        {'name': 'enable_comments', 'type': bool, 'doc': 'enable comments', 'required': False, 'default': True},
        {'name': 'only_authorized_comments', 'type': bool, 'doc': 'only authorized comments', 'required': False,
         'default': False},
        {'name': 'source', 'type': str, 'doc': 'source', 'required': False, 'default': None},
        {'name': 'datetime', 'type': datetime.datetime, 'doc': 'datetime', 'required': False, 'default': None},

    )
    def put(self, title, subtitle, body, category, tags, slug, enable_comments, only_authorized_comments, source, forced_datetime):
        import base.common.orm
        import base.common.sequencer as s
        _session = base.common.orm.orm.session()
        _slug = Post.mkslug(title) if not slug else Post.mkslug(slug)

        _id = s.sequencer().new('p')

        p = Post(_id, self.auth_user.user, title, subtitle, body, slug=_slug, tags=tags,
                 enable_comments=enable_comments,
                 only_authorized_comments=only_authorized_comments,
                 source=source,
                 forced_datetime=forced_datetime,
                 str_category=category)

        _session.add(p)

        base.common.orm.commit()

        return self.ok({'id': p.id})

    def get(self):

        posts = []
        if self.auth_user.user.posts:
            posts = [p.id for p in self.auth_user.user.posts]

        return self.ok({
            'posts': posts
        })



@authenticated()
@api(
    URI='/wiki/posts/tagged_with/:tag'
)
class PostsByTag(Base):
    @params(
        {'name': 'tag', 'type': str, 'doc': 'id', 'required': True}
    )
    def get(self, tag):

        import base.common.orm
        _session = base.common.orm.orm.session()

        db_tag = _session.query(Tag).filter(Tag.name == Tag.tagify(tag)).one_or_none()
        if not db_tag:
            return self.error('tag not found')

        posts = []
        for post in db_tag.posts:
            posts.append({
                'id': post.id,
                'slug': post.slug,
                'author': {
                    'email': post.user.auth_user.username,
                    'first_name': post.user.first_name,
                    'last_name': post.user.last_name
                },
                'title': post.title,
                'created_datetime': str(post.created),
                'updated_datetime': str(post.last_modified_datetime),
                'status': post.id_status
            })

        return self.ok({'posts': posts})


@authenticated()
@api(
    URI='/wiki/posts/:id'
)
class PostById(Base):

    @params(
        {'name': 'id', 'type': str, 'doc': 'id', 'required': True}
    )
    def get(self, _id):

        import base.common.orm
        from src.models.knowledgebase import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id == _id).one_or_none()
        if not p:
            return self.error("Post not found")

        try:
            _body = json.loads(p.body)
        except:
            _body = ''

        return self.ok({
            'author': {
                'email': p.user.auth_user.username,
                'first_name': p.user.first_name,
                'last_name': p.user.last_name
            },
            'title': p.title,
            'body': _body,
            'tags': [t.name for t in p.show_tags],
            'attached_files': get_post_files(p),
            'comments': get_comments(p.id, canonical=True)
        })

    @params(
        {'name': 'id', 'type': str, 'doc': 'id', 'required': True},
        {'name': 'title', 'type': str, 'doc': 'title', 'required': True},
        {'name': 'body', 'type': str, 'doc': 'body', 'required': True},
        {'name': 'tags', 'type': list, 'doc': 'tags', 'required': False, 'default': None},
    )
    def patch(self, _id, title, body, tags):

        import base.common.orm
        from src.models.knowledgebase import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id == _id).one_or_none()
        if not p:
            return self.error("Post not found")

        changed = p.update(self.auth_user.user, title, body, tags)

        if changed:
            base.common.orm.commit()

        return self.ok({'changed': changed})


