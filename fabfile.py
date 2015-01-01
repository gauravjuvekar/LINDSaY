from fabric.api import *
from cuisine import *

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
    with mode_sudo():
        python_package_upgrade_pip("pip")

def install_virtual_envs():
    with mode_sudo():
        python_package_ensure_pip("virtualenvwrapper")


@task
def provision():
    #execute(update_package_cache)
    execute(ensure_core_packages)
    execute(ensure_apache)
    execute(ensure_mysql)
    execute(upgrade_pip)
    execute(install_virtual_envs)

