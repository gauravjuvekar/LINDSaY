from fabric.api import *
from cuisine import *

from base64 import b64encode
import os

env.host_string = 'gaurav@localhost:2022'

env.PROJECT_NAME = "LINDSaY"
env.VIRTUAL_ENV_NAME = env.PROJECT_NAME

env.DJANGO_USERNAME = "djangouser"
env.DJANGO_USER_PASSWORD = b64encode(os.urandom(64))
env.DJANGO_USER_TOPLEVEL = "django_projects"

env.DB_NAME = "django_db"
env.DB_USERNAME = env.DJANGO_USERNAME
env.DB_USER_PASSWORD = b64encode(os.urandom(64))

env.GIT_REPO = "https://github.com/gauravjuvekar/LINDSaY.git"
env.GIT_BRANCH = "prod"

def update_package_cache():
    package_update()


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

def ensure_apache():
    package_list = [
            "apache2",
            "apache2-mpm-prefork",
            "apache2-utils",
            "libapache2-mod-wsgi",
            "libexpat1",
    ]
    package_ensure(package_list)


def ensure_mysql():
    package_list = [
            "mysql-server",
            "libmysqlclient-dev",
    ]
    package_ensure(package_list)


def ensure_requirements_dev_packages():
    package_list = [
            "libldap2-dev",
            "libsasl2-dev",
            "libssl-dev",
    ]
    package_ensure(package_list)

def upgrade_pip():
    execute(ensure_core_packages)
    with mode_sudo():
        python_package_upgrade_pip("pip")

def ensure_virtual_envs():
    execute(upgrade_pip)
    with mode_sudo():
        python_package_ensure_pip("virtualenvwrapper")


@task
def provision():
    #execute(update_package_cache)
    execute(ensure_core_packages)
    execute(ensure_apache)
    execute(ensure_mysql)
    execute(upgrade_pip)
    execute(ensure_virtual_envs)


@task
def setup_db():
    execute(ensure_mysql)
    create_db_command = ("CREATE DATABASE `{DB_NAME}`; ".format(**env))
    grant_db_command = (
            "GRANT ALL PRIVILEGES ON `{DB_NAME}`.* TO `{DB_USERNAME}` "
            "IDENTIFIED BY \"{DB_USER_PASSWORD}\"; "
            "FLUSH PRIVILEGES;"
            .format(**env)
    )
    run("mysql -u root -e '{command}'"
            .format(command=';'.join((create_db_command, grant_db_command)))
    )


def ensure_django_user():
    user_ensure(env.DJANGO_USERNAME, passwd=env.DJANGO_USER_PASSWORD)
    env.DJANGO_USER_HOME_PATH = os.path.join(
            '/', 'home', env.DJANGO_USERNAME,
    )

def ensure_django_user_tree():
    execute(ensure_django_user)
    with mode_user(env.DJANGO_USERNAME):
        top_level_dir = os.path.join(
                env.DJANGO_USER_HOME_PATH,
                env.DJANGO_USER_TOPLEVEL,
        )
        dir_ensure(top_level_dir)
        env.DJANGO_USER_TOPLEVEL_PATH = top_level_dir

def ensure_virtual_env_config():
    execute(ensure_virtual_envs)
    execute(ensure_django_user)

    with settings(sudo_user = env.DJANGO_USERNAME):
        with mode_user(env.DJANGO_USERNAME):
            file_name = os.path.join(env.DJANGO_USER_HOME_PATH,
                    '.profile')
            file_ensure(file_name)
            file_update(
                    file_name,
                    lambda _: text_ensure_line(_,
                            "# Configure virtual envs" ,
                            "export WORKON_HOME="
                            "\"{DJANGO_USER_HOME_PATH}/.virtualenvs\""
                            .format(**env),
                            "source /usr/local/bin/virtualenvwrapper.sh",
                    )
            )


@task
def ensure_project_env():
    execute(ensure_virtual_env_config)
    with settings(sudo_user = env.DJANGO_USERNAME):
        with mode_user(env.DJANGO_USERNAME):
            with prefix('source {}'
                    .format(os.path.join(env.DJANGO_USER_HOME_PATH,'.profile')
                    )
            ):
                run("mkvirtualenv --no-site-packages \"{VIRTUAL_ENV_NAME}\""
                        .format(**env)
                )



