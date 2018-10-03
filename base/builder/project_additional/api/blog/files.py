# coding= utf-8

from base.application.components import Base
from base.application.components import api
from base.application.components import params
from base.application.components import authenticated

import os
import tornado.gen
import tornado.web

from src.models.blog import PostFile

from src.common.common import get_post_files
import tornado.concurrent as concurrent


@authenticated()
@api(
    URI='/wiki/posts/:id/files',
    SPECIFICATION_PATH='Blog'
)
class Files(Base):
    """Manipulate files for a post"""

    @params(
        {'name': 'id', 'type': str, 'doc': 'id', 'required': True},
    )
    def get(self, _id):
        import base.common.orm
        from src.models.blog import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id == _id).one_or_none()
        if not p:
            return self.error("Post not found")

        return self.ok({"files": get_post_files(p)})

    @params(
        {'name': 'id', 'type': str, 'doc': 'id', 'required': True},
        {'name': 'filename', 'type': str, 'doc': 'title', 'required': True},
        {'name': 'local_name', 'type': str, 'doc': 'local_name', 'required': True},
    )
    def put(self, _id, filename, local_name):
        import base.common.orm
        from src.models.blog import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id == _id).one_or_none()
        if not p:
            return self.error("Post not found")

        p.attached_files.append(PostFile(filename, local_name))

        _session.commit()

        return self.ok({"ok": True})

    @params(
        {'name': 'id', 'type': str, 'doc': 'id', 'required': True},
        {'name': 'file_names', 'type': list, 'doc': 'list of files to append', 'required': True},
    )
    def patch(self, _id, file_names):
        import base.common.orm
        from src.models.blog import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id == _id).one_or_none()
        if not p:
            return self.error("Post not found")

        for file in file_names:
            p.attached_files.append(PostFile(file['filename'], file['local_name']))

        _session.commit()

        return self.ok({"ok": True})



@api(
    URI='/posts/files-for-editor',
    SPECIFICATION_PATH='Blog'
)
class SaveFilesForEditor(Base):
    """Save file for the post from the ck editor"""

    @tornado.gen.coroutine
    def post(self):

        import src.config.blog_config as bc
        import uuid

        attach_files = self.request.files.get('upload')
        attached_file = attach_files[0]
        attached_file_name = attached_file['filename']
        attached_file_ext = attached_file_name.split('.')[-1]

        fn = uuid.uuid4()
        file_name = '{}/{}.{}'.format(bc.blog_files_directory, fn, attached_file_ext)
        with open(file_name, 'wb') as f:
            f.write(attached_file['body'])


        # todo: save changes to the database

        yield self.ok({
            'url': '{}/{}.{}'.format(bc.frontend_blog_files_directory, fn, attached_file_ext),
            'uploaded': 1,
            'fileName': attached_file_name
        })


@authenticated()
@api(
    URI='/posts/files',
    SPECIFICATION_PATH='Blog'
)
class SaveFiles(Base):
    """Save file for the post"""

    @tornado.gen.coroutine
    def post(self):

        id_post = self.get_argument('id_post', None)
        if id_post is None:
            return self.error('No post found')

        import src.config.blog_config as bc
        import uuid

        attached_files = []
        attach_files = self.request.files.get('files[]')
        if attach_files is None:
            return self.ok({'result': attached_files})

        for attached_file in attach_files:
            attached_file_name = attached_file['filename']
            attached_file_ext = attached_file_name.split('.')[-1]
            fn = uuid.uuid4()
            file_name = '{}/{}.{}'.format(bc.blog_files_directory, fn, attached_file_ext)
            with open(file_name, 'wb') as f:
                f.write(attached_file['body'])

            attached_files.append(
                {
                    'staticUrl': '{}/{}.{}'.format(bc.frontend_blog_files_directory, fn, attached_file_ext),
                    'uploaded': 1,
                    'fileName': attached_file_name,
                    'localFileName': '{}.{}'.format(fn, attached_file_ext),
                })

        files_to_set = [{'filename': f['fileName'], 'local_name': f['localFileName']} for f in attached_files]

        def set_files(files, _id_post):
        
            import base.common.orm
            from src.models.blog import Post
            _session = base.common.orm.orm.session()

            p = _session.query(Post).filter(Post.id == _id_post).one_or_none()
            if not p:
                return False

            for file in files:
                p.attached_files.append(PostFile(file['filename'], file['local_name']))

            try:
                _session.commit()
            except Exception as e:
                _session.rollback()
                return False

            return True

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)
        
        response = yield executor.submit(set_files, files_to_set, id_post)
        if not response:
            return self.error('Error set files to post')

        return self.ok({'result': attached_files})


@authenticated()
@api(
    URI='/posts/cover',
    SPECIFICATION_PATH='Blog'
)
class SaveCover(Base):
    """Save Cover"""

    @tornado.gen.coroutine
    def post(self):

        id_post = self.get_argument('id_post', None)
        if id_post is None:
            return self.error('No post found')

        attach_files = self.request.files.get('files[]')
        if attach_files is None:
            return self.ok({'result': ''})

        import base.common.orm
        from src.models.blog import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id == id_post).one_or_none()
        if not p:
            return False

        attached_image = attach_files[0]
        cover_directory_for_frontend = '/static/images/blog_img'
        cover_directory_for_save = '{}{}'.format(os.getcwd(), cover_directory_for_frontend)

        attached_file_name = attached_image['filename']
        attached_file_ext = attached_file_name.split('.')[-1]
        fn = '{}_cover.{}'.format(p.slug, attached_file_ext)
        file_name = '{}/{}'.format(cover_directory_for_save, fn)

        with open(file_name, 'wb') as f:
            f.write(attached_image['body'])

        def set_file(file, _id_post):

            import base.common.orm
            from src.models.blog import Post
            _session = base.common.orm.orm.session()

            p = _session.query(Post).filter(Post.id == _id_post).one_or_none()
            if not p:
                return False

            p.cover_img = file

            try:
                _session.commit()
            except Exception as e:
                _session.rollback()
                return False

            return True

        file_name_for_frontend = '{}/{}'.format(cover_directory_for_frontend, fn)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)

        response = yield executor.submit(set_file, file_name_for_frontend, id_post)
        if not response:
            return self.error('Error set files to post')

        return self.ok({'result': file_name_for_frontend})


@authenticated()
@api(
    URI='/posts/thumb',
    SPECIFICATION_PATH='Blog'
)
class SaveThumb(Base):
    """Save Thumb"""

    @tornado.gen.coroutine
    def post(self):

        id_post = self.get_argument('id_post', None)
        if id_post is None:
            return self.error('No post found')

        attach_files = self.request.files.get('files[]')
        if attach_files is None:
            return self.ok({'result': ''})

        import base.common.orm
        from src.models.blog import Post
        _session = base.common.orm.orm.session()

        p = _session.query(Post).filter(Post.id == id_post).one_or_none()
        if not p:
            return False

        attached_image = attach_files[0]
        cover_directory_for_frontend = '/static/images/blog_img'
        cover_directory_for_save = '{}{}'.format(os.getcwd(), cover_directory_for_frontend)

        attached_file_name = attached_image['filename']
        attached_file_ext = attached_file_name.split('.')[-1]
        fn = '{}_thumb.{}'.format(p.slug, attached_file_ext)
        file_name = '{}/{}'.format(cover_directory_for_save, fn)

        with open(file_name, 'wb') as f:
            f.write(attached_image['body'])

        def set_file(file, _id_post):

            import base.common.orm
            from src.models.blog import Post
            _session = base.common.orm.orm.session()

            p = _session.query(Post).filter(Post.id == _id_post).one_or_none()
            if not p:
                return False

            p.tumb_img = file

            try:
                _session.commit()
            except Exception as e:
                _session.rollback()
                return False

            return True

        file_name_for_frontend = '{}/{}'.format(cover_directory_for_frontend, fn)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)

        response = yield executor.submit(set_file, file_name_for_frontend, id_post)
        if not response:
            return self.error('Error set files to post')

        return self.ok({'result': file_name_for_frontend})

