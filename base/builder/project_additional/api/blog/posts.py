# coding= utf-8

import json
import datetime

from base.common.utils import log
from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated

from src.models.blog import Post, Tag, ShowTag
from src.common.common import get_comments
from src.common.common import get_post_files


@authenticated()
@api(
    URI='/wiki/posts',
    SPECIFICATION_PATH='Blog'
)
class AddPost(Base):
    @params(  # if you want to add params
        {'name': 'title', 'type': str, 'doc': 'title', 'required': True},
        {'name': 'subtitle', 'type': str, 'doc': 'subtitle', 'required': False},
        {'name': 'body', 'type': str, 'doc': 'body', 'required': False},
        {'name': 'category', 'type': str, 'doc': 'category', 'required': False},
        {'name': 'tags', 'type': list, 'doc': 'list of tags', 'required': False},
        {'name': 'slug', 'type': str, 'doc': 'slug', 'required': False},
        {'name': 'enable_comments', 'type': bool, 'doc': 'enable comments', 'required': False, 'default': True},
        {'name': 'only_authorized_comments', 'type': bool, 'doc': 'only authorized comments', 'required': False,
         'default': False},
        {'name': 'source', 'type': str, 'doc': 'source', 'required': False, 'default': None},
        {'name': 'datetime', 'type': datetime.datetime, 'doc': 'datetime', 'required': False, 'default': None},
        {'name': 'cover_img', 'type': str, 'doc': 'cover0img', 'required': False},
        {'name': 'tumb_img', 'type': str, 'doc': 'cover0img', 'required': False},
        {'name': 'language', 'type': str, 'doc': 'post language', 'required': False, 'min': 2, 'max': 2,
         'lowercase': True, 'default': 'en'},
        {'name': 'youtube_link', 'type': str, 'doc': 'youtube short code', 'required': False},
        {'name': 'id_group', 'type': int, 'doc': 'group id', 'required': False},
        {'name': 'html_meta', 'type': json, 'doc': 'post html meta tags', 'required': False},
    )
    def put(self, title, subtitle, body, category, tags, slug, enable_comments, only_authorized_comments, source,
            forced_datetime, cover_img, tumb_img, language, youtube_link, id_group, html_meta):
        import base.common.orm
        _session = base.common.orm.orm.session()
        _slug = Post.mkslug(title) if not slug else Post.mkslug(slug)

        _group = None
        if id_group is not None:
            _g = _session.query(Post).filter(Post.id == id_group).one_or_none()
            if _g is not None:
                _group = _g

        _html_meta = None
        if html_meta is not None:
            try:
                _html_meta = json.dumps({
                    'html_meta': html_meta
                }, ensure_ascii=False)
            except Exception as e:
                log.critical('Can not save meta: {}'.format(e))
                return self.error('Error add post')

        import sqlalchemy.exc
        try:
            p = Post(self.auth_user.user, title, subtitle, body, _slug, tags, cover_img, tumb_img, language,
                     enable_comments=enable_comments,
                     only_authorized_comments=only_authorized_comments,
                     source=source,
                     forced_datetime=forced_datetime,
                     str_category=category,
                     youtube_link=youtube_link,
                     group=_group,
                     html_meta=_html_meta)
        except sqlalchemy.exc.IntegrityError as e:
            log.critical('Can not add new post: {}'.format(e))
            if e.orig is not None and e.orig.args is not None:
                if e.orig.args[0] == 1062 and 'post_id_group_lang_ux_1' in e.orig.args[1]:
                    return self.error('Can not add post with the same group and language')
            return self.error('Error add post')

        _session.add(p)

        base.common.orm.commit()

        return self.ok({'id': p.id, 'slug': p.slug})

    def get(self):

        posts = []
        if self.auth_user.user.posts:
            posts = [p.id for p in self.auth_user.user.posts]

        return self.ok({
            'posts': posts
        })


@authenticated()
@api(
    URI='/wiki/check-slug',
    SPECIFICATION_PATH='Blog'
)
class CheckSlugPost(Base):
    @params(
        {'name': 'slug', 'type': str, 'doc': 'slug', 'required': True}
    )
    def get(self, slug):
        _slug = Post.mkslug(slug)

        return self.ok({
            'slug': _slug
        })


@authenticated()
@api(
    URI='/wiki/posts/tagged_with/:tag',
    SPECIFICATION_PATH='Blog'
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
    URI='/wiki/posts/:id/tags',
    SPECIFICATION_PATH='Blog'
)
class PostTags(Base):
    @params(
        {'name': 'id', 'type': int, 'doc': 'id', 'required': True}
    )
    def get(self, _id):
        import base.common.orm
        from src.models.blog import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id == _id).one_or_none()
        if not p:
            return self.error("Post not found")

        return self.ok({'tags': [t.name for t in p.show_tags]})

    @params(
        {'name': 'id', 'type': int, 'doc': 'id', 'required': True},
        {'name': 'tag_name', 'type': str, 'doc': 'id', 'required': True}
    )
    def put(self, _id, tag_name):
        import base.common.orm
        from src.models.blog import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id == _id).one_or_none()
        if not p:
            return self.error("Post not found")

        added = p.tagg_it([tag_name])

        if added>0:
            _session.commit()

        if added==0:
            return self.error('tag already exists')

        return self.ok({'added': added})


@authenticated()
@api(
    URI='/wiki/posts/:id/tags/:show_tag_name',
    SPECIFICATION_PATH='Blog'
)
class PostTagDeleteHandler(Base):
    @params(
        {'name': 'id', 'type': int, 'doc': 'id', 'required': True},
        {'name': 'show_tag_name', 'type': str, 'doc': 'id', 'required': True}
    )
    def delete(self, _id, show_tag_name):
        import base.common.orm
        from src.models.blog import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id == _id).one_or_none()
        if not p:
            return self.error("Post not found")

        show_tag = _session.query(ShowTag).filter(ShowTag.name == show_tag_name).one_or_none()
        if not show_tag:
            return self.error('tag not found')

        p.show_tags.remove(show_tag)

        tag = _session.query(Tag).filter(Tag.name == Tag.tagify(show_tag_name)).one_or_none()
        if tag:
            p.tags.remove(tag)

        _session.commit()

        return self.ok()


@authenticated()
@api(
    URI='/wiki/posts/:id',
    SPECIFICATION_PATH='Blog'
)
class PostById(Base):
    @params(
        {'name': 'id', 'type': int, 'doc': 'id', 'required': True}
    )
    def get(self, _id):

        import base.common.orm
        from src.models.blog import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id == _id).one_or_none()
        if not p:
            return self.error("Post not found")

        try:
            _body = json.loads(p.body)
        except:
            _body = ''

        try:
            _html_meta = json.loads(p.html_meta)
            _html_meta = json.dumps(_html_meta['html_meta'])
        except:
            _html_meta = ''

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
            'comments': get_comments(p.id, canonical=True),
            'html_meta': _html_meta
        })

    @params(
        {'name': 'id', 'type': int, 'doc': 'id', 'required': True},
        {'name': 'title', 'type': str, 'doc': 'title', 'required': False},
        {'name': 'subtitle', 'type': str, 'doc': 'title', 'required': False},
        {'name': 'body', 'type': str, 'doc': 'body', 'required': False},
        {'name': 'tags', 'type': list, 'doc': 'tags', 'required': False, 'default': None},
        {'name': 'category', 'type': str, 'doc': 'category', 'required': False},
        {'name': 'comments_enabled', 'type': bool, 'doc': 'comments_enabled status of post', 'required': False,
         'default': True},
        {'name': 'status', 'type': int, 'doc': 'status of post', 'required': False},
        {'name': 'html_meta', 'type': json, 'doc': 'post html meta tags', 'required': False},
        {'name': 'youtube_link', 'type': str, 'doc': 'youtube link', 'required': False},

    )
    def patch(self, _id, title, subtitle, body, tags, category, comments_enabled, status, html_meta, youtube_link):

        import base.common.orm
        from src.models.blog import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id == _id).one_or_none()
        if not p:
            return self.error("Post not found")

        import src.lookup.post_status as post_status

        if not p.published_time and status == post_status.PUBLISHED:
            p.published_time = datetime.datetime.now()

        _html_meta = None
        if html_meta is not None:
            try:
                _html_meta = json.dumps({
                    'html_meta': html_meta
                }, ensure_ascii=False)
            except Exception as e:
                log.critical('Can not save meta: {}'.format(e))
                return self.error('Error update post')

        changed = p.update(self.auth_user.user, title, subtitle, body, tags, category, comments_enabled, status, 
                            youtube_link, html_meta=_html_meta)

        if changed:
            base.common.orm.commit()

        return self.ok({'changed': changed})


@authenticated()
@api(
    URI='/wiki/posts/group/:id_group',
    SPECIFICATION_PATH='Blog'
)
class PostGroupById(Base):
    @params(
        {'name': 'id_group', 'type': int, 'doc': 'post group id', 'required': True}
    )
    def get(self, _id_group):

        import base.common.orm
        from src.models.blog import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id_group == _id_group)
        _posts = []
        for _p in p:

            try:
                _body = json.loads(_p.body)
            except json.JSONDecodeError:
                _body = ''

            _posts.append({
                'author': {
                    'email': _p.user.auth_user.username,
                    'first_name': _p.user.first_name,
                    'last_name': _p.user.last_name
                },
                'title': _p.title,
                'body': _body,
                'tags': [t.name for t in _p.show_tags],
                'attached_files': get_post_files(_p),
                'comments': get_comments(_p.id, canonical=True)
            })

        return self.ok({'posts': _posts})


@authenticated()
@api(
    URI='/wiki/diff-lang-posts/:lang',
    SPECIFICATION_PATH='Blog'
)
class PostsOnDifferentLanguage(Base):
    """
    Get all group head posts on different languages
    to be able to connect current working post to some group
    """
    @params(
        {'name': 'lang', 'type': str, 'doc': 'category', 'required': True},
        {'name': 'category', 'type': str, 'doc': 'category', 'required': False}
    )
    def get(self, lang, category):

        import base.common.orm
        from src.models.blog import Post
        _session = base.common.orm.orm.session()

        if category is None:
            posts = _session.query(Post).filter(Post.id_group == Post.id, Post.language != lang).all()
        else:
            posts = _session.query(Post).filter(Post.id_group == Post.id, Post.language != lang, Post.category == category).all()

        _posts = []
        for p in posts:
            _posts.append({'title': p.title, 'id_group': p.id_group})

        return self.ok({'posts': _posts})
