# coding= utf-8

import json
import timeago
import datetime
import sqlalchemy
from slugify import slugify
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, Text, CHAR, Date
from sqlalchemy.orm import relationship

import base.common.orm

from src.models.user import User

# Tags are using for search the posts

post2tag = sqlalchemy.Table('post2tag', base.common.orm.sql_base.metadata,
                            sqlalchemy.Column('id_post', CHAR(10), sqlalchemy.ForeignKey('posts.id'), index=True),
                            sqlalchemy.Column('id_tag', Integer, sqlalchemy.ForeignKey('tags.id'), index=True),
                            sqlalchemy.UniqueConstraint('id_post', 'id_tag', name='post2tag_uix_1')
                            )

# showtags are used to display tags, because #taggIt is same tag like #taggit but if author want to have
# taggIt below post we will allow him that.

post2showtag = sqlalchemy.Table('post2showtag', base.common.orm.sql_base.metadata,
                                sqlalchemy.Column('id_post', CHAR(10), sqlalchemy.ForeignKey('posts.id'), index=True),
                                sqlalchemy.Column('id_showtag', Integer, sqlalchemy.ForeignKey('show_tags.id'),
                                                  index=True),
                                sqlalchemy.UniqueConstraint('id_post', 'id_showtag', name='post2showtag_uix_1')
                                )


class PostStatus(base.common.orm.sql_base):
    """Status of the post, e.g. PUBLISHED, CHECKED...."""

    __tablename__ = 'lookup_post_statuses'

    id = Column(Integer, primary_key=True)
    text = Column(String(64), unique=True, nullable=False)

    def __init__(self, id, text):
        self.id = id
        self.text = text


class PostCategory(base.common.orm.sql_base):
    """Status of the post, e.g. PUBLISHED, CHECKED...."""

    __tablename__ = 'lookup_post_categories'

    id = Column(Integer, autoincrement=True, primary_key=True)
    text = Column(String(64), unique=True, nullable=False)

    def __init__(self, text):
        self.text = text

    @staticmethod
    def all(_session):
        db_categories = _session.query(PostCategory).all()
        categories = []
        for db_category in db_categories:
            categories.append({
                'name': db_category.text,
            })
        return categories


class FileType(base.common.orm.sql_base):
    """Types of uploaded and attached files with types descriptions"""

    __tablename__ = 'file_types'

    id = Column(CHAR(8), primary_key=True)
    description = Column(String(255), nullable=True)

    def __init__(self, id, description):
        self.id = id
        self.description = description


class ArchivedPostRevision(base.common.orm.sql_base):
    """Archived state of the post after change"""

    __tablename__ = 'archived_post_revisions'

    id = Column(Integer, autoincrement=True, primary_key=True)
    id_post = Column(CHAR(10), ForeignKey('posts.id'), index=True)
    post = relationship("Post", uselist=False, back_populates="archived_revisions", foreign_keys=[id_post])

    created = Column(DateTime, nullable=False)
    id_user = Column(CHAR(10), ForeignKey(User.id))

    post_slug = Column(String(255), nullable=True)
    post_id_user = Column(CHAR(10), ForeignKey(User.id), nullable=True)
    post_created = Column(DateTime, nullable=True)
    post_created_date = Column(Date, nullable=True)
    post_removed = Column(Boolean, nullable=True)
    post_id_status = Column(Integer, nullable=True)
    post_title = Column(String(255), nullable=True)
    post_body = Column(Text, nullable=True)

    post_show_tags = Column(Text)

    def __init__(self, post):
        self.post = post
        self.id_user = post.id_user_modified
        self.created = post.last_modified_datetime
        self.post_slug = post.slug
        self.post_title = post.title
        self.post_body = post.body

        post_show_tags = []
        for show_tag in post.show_tags:
            post_show_tags.append(show_tag.id)

        self.post_show_tags = str(post_show_tags).replace(' ', '')[1:-1]


class PostFile(base.common.orm.sql_base):
    """Files attached to posts - details. Content is kept somewhere else."""

    __tablename__ = 'post_files'

    id = Column(Integer, autoincrement=True, primary_key=True)
    id_post = Column(CHAR(10), ForeignKey('posts.id'), index=True)
    id_user = Column(CHAR(10), ForeignKey(User.id), index=True)
    full_filename = Column(String(255), nullable=False)
    local_filename = Column(String(255), nullable=False)

    id_filetype = Column(String(8), ForeignKey(FileType.id), nullable=True)
    filetype = relationship("FileType", foreign_keys=[id_filetype])

    file_size = Column(Integer, nullable=False)
    created = Column(DateTime, nullable=False)

    md5 = Column(String(32), nullable=True)

    removed = Column(DateTime, nullable=True)

    posts = relationship("Post", back_populates="attached_files", foreign_keys=[id_post])
    user = relationship("User", foreign_keys=[id_user])
    source_ckeditor = Column(Boolean, default=False, nullable=False)

    def __init__(self, full_filename, local_filename, file_size=-1, source_ckeditor=False):
        self.file_size = file_size

        self.full_filename = full_filename
        self.local_filename = local_filename
        self.created = datetime.datetime.now()
        self.source_ckeditor = source_ckeditor

        extension = full_filename.split('.')[-1].strip().lower() \
            if full_filename.find('.') != -1 else None

        import base.common.orm
        _session = base.common.orm.orm.session()

        ft = _session.query(FileType).filter(FileType.id == extension).one_or_none()

        if not ft:
            ft = FileType(extension, extension)
            _session.add(ft)

        self.filetype = ft


class Post(base.common.orm.sql_base):
    __tablename__ = 'posts'

    id = Column(CHAR(10), primary_key=True)

    slug = Column(String(255), nullable=True, unique=True)

    id_user = Column(CHAR(10), ForeignKey(User.id), index=True)

    id_user_modified = Column(CHAR(10), ForeignKey(User.id), index=True)

    created = Column(DateTime, nullable=False)
    published_time = Column(DateTime, nullable=True, default=None)
    created_date = Column(Date, nullable=False, index=True)
    last_modified_datetime = Column(DateTime, nullable=False)

    removed = Column(Boolean, index=True, default=False, nullable=False)

    id_status = Column(Integer, ForeignKey(PostStatus.id), index=True)
    status = sqlalchemy.orm.relationship('PostStatus')

    id_category = Column(Integer, ForeignKey(PostCategory.id), index=True, nullable=True)
    category = sqlalchemy.orm.relationship('PostCategory')

    title = Column(String(255), nullable=False, index=True)
    subtitle = Column(String(255), nullable=True, default=None)

    cover_img = Column(String(255), nullable=True, default=None)
    tumb_img = Column(String(255), nullable=True, default=None)

    body = Column(Text)

    comments_enabled = Column(Boolean, nullable=False, default=True)
    comments_restriction_only_authorized = Column(Boolean, nullable=False, default=False)

    comments_verified_only = Column(Boolean, nullable=False, default=False)  # TODO: Implement

    user = relationship("User", back_populates="posts", foreign_keys=[id_user])
    last_modified_by = relationship("User", foreign_keys=[id_user_modified])

    comments = relationship("Comment", back_populates="post")

    attached_files = relationship("PostFile", back_populates="posts")  # TODO, dodati uslov da nisu removed - query
    archived_revisions = relationship("ArchivedPostRevision", back_populates="post")
    tags = sqlalchemy.orm.relationship('Tag', secondary=post2tag, backref='Post')
    show_tags = sqlalchemy.orm.relationship('ShowTag', secondary=post2showtag, backref='Post')

    source = Column(Text, nullable=True, default=None)

    published = Column(Boolean, default=False, nullable=False)

    def get_comments(self, canonical=True):

        comments = []

        for db_comment in self.comments:  # q_comments:
            comments.append({'authorized': db_comment.id_user is not None,
                             'author': db_comment.user.auth_user.username if db_comment.id_user else db_comment.display_name_of_unauthorized_user,
                             'created': str(db_comment.created),
                             'id': db_comment.id,
                             'id_parent_comment': db_comment.id_parent_comment,
                             'text': db_comment.text,
                             'comments_approved': db_comment.comment_approved
                             })

        comments.sort(key=lambda x: x['created'], reverse=False)

        if canonical:
            ccomments = {}
            parents = {}
            for c in comments:
                if not c['id_parent_comment']:
                    del c['id_parent_comment']
                    ccomments[c['id']] = c
                    ccomments[c['id']]['children'] = {}
                    parents[c['id']] = ccomments[c['id']]
                else:
                    id_parent = c['id_parent_comment']
                    del c['id_parent_comment']
                    if id_parent not in parents:
                        return False, "Invalid parent/child structure"

                    parents[id_parent]['children'][c['id']] = c
                    parents[id_parent]['children'][c['id']]['children'] = {}
                    parents[c['id']] = parents[id_parent]['children'][c['id']]

            return ccomments

        return comments

    def get_post_body(self):
        return json.loads(self.body)

    def ago(self):

        now = datetime.datetime.now() + datetime.timedelta(seconds=60 * 3.4)
        _created = self.created if not self.published_time else self.published_time
        return timeago.format(_created, now)

    def iso_date(self):
        return self.created.strftime("%Y-%m-%d")

    def display_date(self):

        return self.created.strftime("%a %d %b %y")

    @staticmethod
    def slug_available(slug):

        import base.common.orm
        _session = base.common.orm.orm.session()

        post = _session.query(Post).filter(Post.slug == slug).one_or_none()

        return post is None

    @staticmethod
    def mkslug(bslug):

        bslug = slugify(bslug).replace('#', '')
        slug = bslug
        iter = 0
        while not Post.slug_available(slug):
            iter += 1
            slug = '{}-{}'.format(bslug, iter)

        return slug

    def update(self, user, title, subtitle, body, tags, category, comments_enabled, published):  # , slug):

        changed = []
        apr = ArchivedPostRevision(self)

        if title is None:
            title = self.title
        if subtitle is None:
            subtitle = self.subtitle
        if body is None:
            body = self.body

        if category is None:
            pass
            # if self.category:
            #     changed.append('category set to none')
            #     self.category = None
        else:
            import base.common.orm
            _session = base.common.orm.orm.session()
            pc = _session.query(PostCategory).filter(PostCategory.text == category).one_or_none()
            if not pc:
                pc = PostCategory(category)
                _session.add(pc)
                changed.append('added category')

            self.category = pc
            changed.append('category')

        if self.title != title:
            self.title = title
            changed.append('title')

        if self.subtitle != subtitle:
            self.subtitle = subtitle
            changed.append('subtitle')

        if self.body != body:
            self.body = json.dumps(body)
            changed.append('body')

        if self.comments_enabled != comments_enabled:
            print(self.comments_enabled)
            self.comments_enabled = comments_enabled
            changed.append('comments_enabled')

        if self.published != published:
            self.published = published
            changed.append('published')

        if tags is not None:

            orig_show_tags = set([t for t in self.show_tags])
            new_show_tags = set(tags)

            if len(tags) != len(orig_show_tags) or new_show_tags != orig_show_tags:
                self.clear_tags()
                self.tagg_it(tags)
                changed.append('tags')

        if len(changed) > 0:
            self.archived_revisions.append(apr)
            self.last_modified_by = user
            self.last_modified_datetime = datetime.datetime.now()

        return changed

    def clear_tags(self):

        # double for, to copy first, because delete will not work proprely on references
        for t in [t for t in self.tags]:
            self.tags.remove(t)

        for t in [t for t in self.show_tags]:
            self.show_tags.remove(t)

    def tagg_it(self, tags):

        import base.common.orm
        _session = base.common.orm.orm.session()

        for src_str_tag in tags:
            str_tag = Tag.tagify(src_str_tag)

            tag = _session.query(Tag).filter(Tag.name == str_tag).one_or_none()
            if not tag:
                tag = Tag(str_tag)

            show_tag = _session.query(ShowTag).filter(ShowTag.name == src_str_tag).one_or_none()
            if not show_tag:
                show_tag = ShowTag(src_str_tag)

            self.tags.append(tag)
            self.show_tags.append(show_tag)

    def __init__(self, id, user, title, subtitle, body, slug, tags, cover_img, tumb_img,
                 enable_comments=True,
                 only_authorized_comments=False,
                 source=None, forced_datetime=None,
                 str_category=None):

        self.cover_img = cover_img
        self.tumb_img = tumb_img

        self.id = id
        self.user = user
        self.last_modified_by = user

        self.created = datetime.datetime.now() if not forced_datetime else forced_datetime
        self.created_date = self.created.date()

        self.last_modified_datetime = self.created

        self.slug = slug
        self.title = title
        self.subtitle = subtitle
        self.body = json.dumps(body, ensure_ascii=False)

        self.tagg_it(tags)
        self.comments_enabled = enable_comments
        self.comments_restriction_only_authorized = only_authorized_comments
        self.source = source

        if str_category:
            import base.common.orm
            _session = base.common.orm.orm.session()

            pc = _session.query(PostCategory).filter(PostCategory.text == str_category).one_or_none()

            if not pc:
                pc = PostCategory(str_category)
                _session.add(pc)

            self.category = pc


class Comment(base.common.orm.sql_base):
    """Comments related to posts"""

    __tablename__ = 'comments'

    id = Column(Integer, autoincrement=True, primary_key=True)
    id_post = Column(CHAR(10), ForeignKey(Post.id), index=True)
    id_user = Column(CHAR(10), ForeignKey(User.id), index=True, nullable=True, default=None)

    created = Column(DateTime, nullable=False)
    text = Column(Text, nullable=False)
    id_parent_comment = Column(Integer, ForeignKey("comments.id"), nullable=True, default=None)

    id_user_approved = Column(CHAR(10), ForeignKey(User.id), nullable=True, default=None)
    approved_datetime = Column(DateTime, nullable=True, default=None)

    post = relationship("Post", back_populates="comments", foreign_keys=[id_post])
    user = relationship("User", back_populates="comments", foreign_keys=[id_user])

    email_of_unauthorised_user = Column(String(64), nullable=True, default=None)
    display_name_of_unauthorized_user = Column(String(64), nullable=True, default=None)

    removed = Column(DateTime, nullable=True, default=None)
    id_user_removed = Column(CHAR(10), ForeignKey(User.id), nullable=True, default=None)

    user_approved = relationship("User", back_populates="approved_comments", foreign_keys=[id_user_approved])

    comment_approved = Column(Boolean, default=False, nullable=False)

    def author_display_name(self):

        if self.id_user:
            return self.user.author_display_name()

        if self.email_of_unauthorised_user:
            return self.email_of_unauthorised_userz

        return "n/a"

    def __init__(self, user, post, text, parent_comment):
        self.created = datetime.datetime.now()
        if user:
            self.user = user

        self.post = post
        self.text = text

        if parent_comment:
            self.id_parent_comment = parent_comment.id


class Tag(base.common.orm.sql_base):
    """Unique tag names"""

    __tablename__ = 'tags'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    posts = sqlalchemy.orm.relationship('Post', secondary=post2tag, backref='Tag')

    @staticmethod
    def tagify(s):
        return s.lower().replace('#', '').replace(' ', '')

    def count(self):
        return len(self.posts)

    def __init__(self, name):
        self.name = Tag.tagify(name)

    @staticmethod
    def all(_session):
        db_tags = _session.query(Tag).all()
        tags = []
        for db_tag in db_tags:
            tags.append({
                'name': db_tag.name,
                'count': len(db_tag.posts)
            })
        return tags


class ShowTag(base.common.orm.sql_base):
    """Viewable version of tags"""

    __tablename__ = 'show_tags'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    posts = sqlalchemy.orm.relationship('Post', secondary=post2showtag, backref='ShowTag')

    def count(self):
        return len(self.posts)

    def __init__(self, name):
        self.name = name


def main():
    import base.common.orm
    from src.models.sequencers import Sequencer
    _session = base.common.orm.orm.session()
    _session.add(PostStatus(1, 'Draft'))
    _session.add(PostStatus(2, 'In Review'))
    _session.add(PostStatus(3, 'Final'))
    _seq = Sequencer('p', '00', '000', 4, 0, 'posts', 'STR', 's_posts', False)
    _session.add(_seq)
    _session.commit()


if __name__ == '__main__':
    main()
