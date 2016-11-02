from distutils.core import setup


setup(
    name='base',
    version='1.00.0',
    packages=['base',
              'base.common',
              'base.config',
              'base.builder',
              'base.builder.project_additional',
              'base.builder.template_project',
              'base.builder.template_project.src',
              'base.builder.template_project.src.api',
              'base.builder.template_project.src.api.utils',
              'base.builder.template_project.src.api.auth_user',
              'base.builder.template_project.src.config',
              'base.builder.template_project.src.lookup',
              'base.application',
              'base.application.lookup',
              'base.application.helpers'],
    url='https://github.com/digital-cube/BASE',
    license='GNU',
    author='Digitl Cube doo',
    author_email='slobodan@digitalcube.rs',
    description='Base, simple scaling project',
    install_requires=['tornado', 'bcrypt'],
    data_files=[('/usr/local/bin', ['base/bin/basemanager']), ],
)
