# coding= utf-8
import os

_home_dir = os.getenv('HOME')
blog_files_directory = '{}/storage/blog'.format(_home_dir) if _home_dir is not None else '/storage/blog'
frontend_blog_files_directory = '/assets/storage/blog'
