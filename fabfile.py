from fabric.api import *
from cuisine import *
from fabvenv import virtualenv

from base64 import b64encode
import os


##############################################################################
# Configuration
##############################################################################
env.host_string = 'gaurav@localhost:2022'

env.PROJECT_NAME = "LINDSaY"
env.APP_NAME = "mesg"
env.PROJECT_NAME_PATHS = env.PROJECT_NAME.lower()

env.VIRTUAL_ENV_NAME = env.PROJECT_NAME 
env.VIRTUAL_ENV_CONFIG_FILE = '.profile'
env.RUNTIME_CONFIG_FILE = "runtime_configuration.py"

env.DJANGO_USERNAME = "djangouser"
env.DJANGO_USER_TOPLEVEL = "django_projects"

env.SECRET_KEY = b64encode(os.urandom(64))
env.KEEP_EXISTING_SECRET_KEY = True

env.SITE_NAME = 'lindsay.com'
env.ALLOWED_HOSTS = ['*']
env.STATIC_ROOT = os.path.join('/', 'var', 'www',
        env.SITE_NAME, 'static'
)
env.STATIC_URL = '/static'
# Media root defined in project root path
#env.MEDIA_ROOT = os.path.join('/', 'var', 'www',
        #env.SITE_NAME, 'media'
#)
env.MEDIA_URL = '/media'
env.SERVER_ADMIN_MAIL = 'webmaster@localhost'
env.WSGI_SCRIPT_PATH = os.path.join('/', 'var', 'www',
        env.SITE_NAME, 'index.wsgi'
)

env.DB_NAME = "django_db"
env.DB_USERNAME = env.DJANGO_USERNAME
env.DB_USER_PASSWORD = b64encode(os.urandom(64))

env.GIT_REPO = "https://github.com/gauravjuvekar/LINDSaY.git"
env.GIT_BRANCH = "prod"


##############################################################################
# Extending fabric
##############################################################################

def once(func):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)

    wrapper.has_run = False
    return wrapper

class sudo_login:
    """
    Executes sudo with -i (as a login shell)
    """
    def __init__(self, sudo_user):
        self.user = sudo_user
    def __enter__(self):
        self.old_sudo_prefix = env.sudo_prefix
        self.old_sudo_user, env.sudo_user = env.sudo_user, self.user
        env.sudo_prefix = "sudo -S -i -p '%(sudo_prompt)s' " 
    def __exit__(self, a, b, c):
        env.sudo_prefix = self.old_sudo_prefix
        env.sudo_user = self.old_sudo_user

##############################################################################
# Packages
##############################################################################


@once
def update_package_cache():
    """
    apt-get update
    """
    package_update()


@once
def ensure_core_packages():
    package_list = [
            "coreutils",
            "python",
            "python-pip",
            "python-dev",
            "build-essential",
            "git",
            "ufw",
            "iptables",
            "openssl",
    ]
    package_ensure(package_list)


@once
def ensure_apache():
    package_list = [
            "apache2",
            "apache2-mpm-prefork",
            "apache2-utils",
            "libapache2-mod-wsgi",
            "libexpat1",
    ]
    package_ensure(package_list)


@once
def ensure_mysql():
    package_list = [
            "mysql-server",
    ]
    package_ensure(package_list)


@once
def ensure_requirements_dev_packages():
    """
    Requred when pip compiles some packages further down
    """
    package_list = [
            "libmysqlclient-dev",
            "libldap2-dev",
            "libsasl2-dev",
            "libssl-dev",
    ]
    package_ensure(package_list)


@once
def upgrade_pip():
    execute(ensure_core_packages)
    with mode_sudo():
        python_package_upgrade_pip("pip")


@once
def ensure_virtual_envs():
    execute(upgrade_pip)
    with mode_sudo():
        python_package_ensure_pip("virtualenvwrapper")


@once
@task
def provision():
    execute(update_package_cache)
    execute(ensure_core_packages)
    execute(ensure_apache)
    execute(ensure_mysql)
    execute(upgrade_pip)
    execute(ensure_requirements_dev_packages)
    execute(ensure_virtual_envs)


##############################################################################
# Django user
##############################################################################

@once
def ensure_django_user():
    user_ensure(env.DJANGO_USERNAME)
    # Use bash as virtualenvs would mostly be configured in .bashrc
    sudo("chsh -s /bin/bash {DJANGO_USERNAME}".format(**env))
    env.DJANGO_USER_HOME_PATH = os.path.join('/', 'home', env.DJANGO_USERNAME)


@once
def ensure_django_user_tree():
    execute(ensure_django_user)
    with settings(sudo_user = env.DJANGO_USERNAME):
        with mode_user(env.DJANGO_USERNAME):
            top_level_dir = os.path.join(
                    env.DJANGO_USER_HOME_PATH,
                    env.DJANGO_USER_TOPLEVEL,
            )
            dir_ensure(top_level_dir)
            env.DJANGO_USER_TOPLEVEL_PATH = top_level_dir


@once
def ensure_virtual_env_config():
    execute(ensure_virtual_envs)
    execute(ensure_django_user)

    with sudo_login(env.DJANGO_USERNAME):
        with mode_user(env.DJANGO_USERNAME):
            file_name = os.path.join(
                    env.DJANGO_USER_HOME_PATH,
                    env.VIRTUAL_ENV_CONFIG_FILE,
            )
            file_ensure(file_name)
            file_update(
                    file_name,
                    lambda _: text_ensure_line(_,
                            "# Configure virtual envs" ,
                            "export WORKON_HOME="
                            "\"{DJANGO_USER_HOME_PATH}/.virtualenvs\""
                            .format(**env),
                            ". /usr/local/bin/virtualenvwrapper.sh",
                    )
            )
            env.VIRTUAL_ENV_CONFIG_FILE_PATH = file_name


##############################################################################
# Virtual env
##############################################################################

@once
def ensure_project_env():
    execute(ensure_virtual_env_config)
    with sudo_login(env.DJANGO_USERNAME):
        with mode_user(env.DJANGO_USERNAME):
            env.WORKON = os.path.join(
                    env.DJANGO_USER_HOME_PATH,
                    '.virtualenvs',
                    env.VIRTUAL_ENV_NAME,
            )
            if not dir_exists(env.WORKON):
                run("mkvirtualenv --no-site-packages \"{VIRTUAL_ENV_NAME}\""
                        .format(**env)
                )
            env.VIRTUAL_ENV_SITE_PACKAGES = os.path.join(
                    env.WORKON,
                    'local', 'lib', 'python-2.7', 'site-packages',
            )
            env.VIRTUAL_ENV_ACTIVATE_PATH = os.path.join(
                    env.WORKON,
                    'bin', 'activate_this.py',
            )


##############################################################################
# Project code and dependencies
##############################################################################

@once
def ensure_code():
    execute(ensure_project_env)
    execute(ensure_django_user_tree)
    with sudo_login(env.DJANGO_USERNAME):
        with mode_user(env.DJANGO_USERNAME):
            with virtualenv(env.WORKON):
                env.DJANGO_PROJECT_PATH = os.path.join(
                        env.DJANGO_USER_TOPLEVEL_PATH,
                        env.PROJECT_NAME,
                )
                if dir_exists(env.DJANGO_PROJECT_PATH):
                    with cd(env.DJANGO_PROJECT_PATH):
                        run("git checkout --force {GIT_BRANCH}".format(**env))
                        run("git pull origin {GIT_BRANCH}".format(**env))
                else:
                    with cd(env.DJANGO_USER_TOPLEVEL_PATH):
                        run("git clone {GIT_REPO} --branch {GIT_BRANCH}"
                                .format(**env)
                        )

                env.PROJECT_MANAGE_PY_DIR = os.path.join(
                        env.DJANGO_PROJECT_PATH,
                        env.PROJECT_NAME_PATHS,
                )
                env.MEDIA_ROOT = os.path.join(env.DJANGO_PROJECT_PATH,'media')
                dir_ensure(env.MEDIA_ROOT) 


@once
def ensure_project_deps():
    execute(ensure_requirements_dev_packages)
    execute(ensure_code)
    with sudo_login(env.DJANGO_USERNAME):
        with mode_user(env.DJANGO_USERNAME):
            with virtualenv(env.WORKON):
                with cd(env.DJANGO_PROJECT_PATH):
                    python_package_ensure_pip(r="requirements.txt")


@once
def ensure_project_configuration():
    execute(ensure_project_deps)
    with sudo_login(env.DJANGO_USERNAME):
        with mode_user(env.DJANGO_USERNAME):
            with cd(env.DJANGO_PROJECT_PATH):
                file_ensure("__init__.py")
                file_ensure(env.RUNTIME_CONFIG_FILE)

                if env.KEEP_EXISTING_SECRET_KEY:
                    previous_key = text_get_line(
                            file_read(env.RUNTIME_CONFIG_FILE),
                            lambda _:_.startswith("SECRET_KEY")
                    ).partition("=")[2].strip('"\'')
                    if (previous_key != '') and (len(previous_key) > 16):
                        env.SECRET_KEY = previous_key

                file_write(
                        env.RUNTIME_CONFIG_FILE,
                        text_template(
                                text_strip_margin(
                                    """
|SECRET_KEY='${SECRET_KEY}'
|ALLOWED_HOSTS=${ALLOWED_HOSTS}
|DATABASE_NAME='${DB_NAME}'
|DATABASE_USER='${DB_USERNAME}'
|DATABASE_PASSWORD='${DB_USER_PASSWORD}'
|STATIC_ROOT='${STATIC_ROOT}'
|STATIC_URL='${STATIC_URL}/'
|MEDIA_ROOT='${MEDIA_ROOT}'
|MEDIA_URL='${MEDIA_URL}/'
                                    """
                                ), env
                        )
                )

##############################################################################
# Database
##############################################################################

@once
def ensure_db():
    execute(ensure_mysql)
    create_db_command = (
            "CREATE DATABASE IF NOT EXISTS `{DB_NAME}`; " .format(**env)
    )
    grant_db_command = (
            "GRANT ALL PRIVILEGES ON `{DB_NAME}`.* TO `{DB_USERNAME}` "
            "IDENTIFIED BY \"{DB_USER_PASSWORD}\"; "
            "FLUSH PRIVILEGES;"
            .format(**env)
    )
    run("mysql -u root -e '{command}'"
            .format(command=';'.join((create_db_command, grant_db_command)))
    )


@once
@task
def sync_db():
    execute(ensure_db)
    execute(ensure_project_configuration)
    with sudo_login(env.DJANGO_USERNAME):
        with mode_user(env.DJANGO_USERNAME):
            with virtualenv(env.WORKON):
                with cd(env.PROJECT_MANAGE_PY_DIR):
                    run("python manage.py makemigrations {APP_NAME}"
                            .format(**env)
                    )

                    run("python manage.py migrate {APP_NAME}"
                            .format(**env)
                    )
                    run("python manage.py syncdb")

##############################################################################
# Web server
##############################################################################

def restart_web_server():
    sudo("apache2ctl restart")


@once
def configure_virtual_host():
    execute(ensure_apache)
    execute(ensure_project_configuration)
    with mode_sudo():
        with cd(os.path.join('/', 'etc', 'apache2', 'sites-available')):
            file_write(
                    '.'.join([env.SITE_NAME, 'conf']),
                    text_template(
                            text_strip_margin(
                                    """
|<VirtualHost *:80>
|    ServerAdmin ${SERVER_ADMIN_MAIL}
|    ServerName ${SITE_NAME}
|    ServerAlias www.${SITE_NAME}
|
|    WSGIScriptAlias / ${WSGI_SCRIPT_PATH}
|
|    Alias ${STATIC_URL} ${STATIC_ROOT}
|    Alias ${MEDIA_URL} ${MEDIA_ROOT}
|    <Location "${STATIC_URL}">
|        Options -Indexes
|    </Location>
|</VirtualHost>
                                    """
                            ), env
                    )
            )


@once
def configure_wsgi():
    with mode_sudo():
        with cd(os.path.join('/', 'var', 'www')):
            dir_ensure(env.SITE_NAME)
            with cd(env.SITE_NAME):
                file_write(
                        "index.wsgi",
                        text_template(
                                text_strip_margin(
                                        """
|import os
|import sys
|import site
|
|site.addsitedir('${VIRTUAL_ENV_SITE_PACKAGES}')
|sys.path.append('${PROJECT_MANAGE_PY_DIR}')
|os.environ['DJANGO_SETTINGS_MODULE'] = '${PROJECT_NAME_PATHS}.settings'
|activate_env = '${VIRTUAL_ENV_ACTIVATE_PATH}'
|execfile(activate_env, dict(__file__ = activate_env))
|
|from django.core.wsgi import get_wsgi_application
|application = get_wsgi_application()
|
                                        """
                                ), env
                        )
                )

@once
def collect_static():
    execute(configure_wsgi)
    with virtualenv(env.WORKON):
        with cd(env.PROJECT_MANAGE_PY_DIR):
            sudo("python manage.py collectstatic --noinput")


def enable_site():
    execute(configure_virtual_host)
    execute(configure_wsgi)
    execute(collect_static)
    sudo("a2dissite 000-default.conf")
    sudo("a2ensite {SITE_NAME}.conf".format(**env))
    execute(restart_web_server)


##############################################################################
# Tasks
##############################################################################

@task
def deploy():
    execute(provision)
    execute(sync_db)
    execute(enable_site)
