# coding= utf-8

from src.models.blog import Comment
import src.config.blog_config as bc


def get_comments(id_post, canonical=False):
    # returns status, err msg | result

    import base.common.orm
    from src.models.blog import Post
    _session = base.common.orm.orm.session()

    p = _session.query(Post).filter(Post.id == id_post).one_or_none()
    if not p:
        return False, "Post not found"

    return True, p.get_comments(canonical=canonical)


def add_comment(id_post, text, id_parent_comment, user, unauthorized_user_email, unauthorized_display_name, self):
    import base.common.orm
    from src.models.blog import Post
    _session = base.common.orm.orm.session()

    p = _session.query(Post).filter(Post.id == id_post).one_or_none()
    if not p:
        return self.error("Post not found")

    if not p.comments_enabled:
        return self.error("Comments are not enabled for this post")

    if p.comments_restriction_only_authorized and user is None:
        return self.error("Only authorized user can comment this post")

    pcomment = None
    if id_parent_comment:

        pcomment = _session.query(Comment).filter(Comment.id == id_parent_comment,
                                                  Comment.id_post == id_post).one_or_none()

        if not pcomment:
            return self.error("Parent comment not found, or not member of the same post")

    c = Comment(user, p, text, pcomment)

    if unauthorized_user_email and not user:
        c.email_of_unauthorised_user = unauthorized_user_email

    if unauthorized_display_name and not user:
        c.display_name_of_unauthorized_user = unauthorized_display_name

    _session.add(c)
    _session.commit()

    return self.ok({"id": c.id})


def get_post_files(post):
    files = []
    for file in post.attached_files:
        files.append({
            'id': file.id,
            'name': file.full_filename,
            'type': file.filetype.description,
            'size': file.file_size,
            'url': '{}/{}'.format(bc.frontend_blog_files_directory, file.local_filename)
        })

    return files

def change_comment_status(approved, id_post, id_comment, self):
    import base.common.orm
    _session = base.common.orm.orm.session()

    comment = _session.query(Comment).filter(Comment.id == id_comment,
                                                  Comment.id_post == id_post).one_or_none()

    if not comment:
        return self.error("Comment not found!")

    comment.comment_approved = approved

    _session.commit()

    return self.ok(
        {"comment": comment.comment_approved, 'id': comment.id})


