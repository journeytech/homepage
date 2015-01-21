from fabric.api import task, run, require, put, local, env
import os
arun = run


env.hosts = ['root@journeytech.vn']

def deploy():
    "Deploy current branch to remote server"
    Deploy.deploy()

def setup():
    "Setup remote server before deploy"
    Deploy.setup()

def update():
    "Update local"
    Deploy.update_local()

def test():
    "Testing commands"
    print Deploy.get_python_version()

def restart_web():
    "Restart web service"
    Deploy.init()
    Deploy.restart_web_services()

def init_folder_tree():
    "Init folder tree"
    Deploy.init_folder_tree()

def update_remote():
    "Update remote source code"
    Deploy.init()
    Deploy.update_remote_code()
    Deploy.collect_current_statics()

def manage(command):
    "Run manage command"
    Deploy.init()
    Deploy.manage(command)

class Deploy(object):

    @classmethod
    def manage(cls, command):
        cls.run_virtualenv("cd %s; python manage.py %s" % (cls.current_dir, command))

    @classmethod
    def run(cls, command):
        return run(command)

    @classmethod
    def init(cls):
        cls.project_name = 'journeytech.vn'
        cls.deploy_dir = '/var/www/journeytech.vn'
        cls.current_dir = '/var/www/journeytech.vn/current'
        cls.share_dir = '/var/www/journeytech.vn/shared'
        cls.bin_dir = '%s/bin' % cls.share_dir
        cls.program_dir = "%s/program" % cls.share_dir
        cls.log_dir = "%s/log" % cls.share_dir
        cls.virtualenv_dir = '/var/www/journeytech.vn/shared/virtualenv'
        cls.git_source = "git@github.com:journeytech/journeytech.git"
        cls.have_yum = cls.is_command_exists('yum')

    @classmethod
    def update_remote_code(cls):
        run("cd %s; git pull origin %s" % (cls.current_dir, cls.branch()))

    @classmethod
    def install_git(cls):
        if not cls.is_command_exists('git'):
            if cls.have_yum:
                run("yum install git -y")
            else:
                run("apt-get install git -y")

    @classmethod
    def is_command_exists(cls, command):
        return len(run("whereis %s" % command)) > len("%s: " % command)

    @classmethod
    def get_command_real_path(cls, command):
        path = run("which %s" % command)
        return path

    @classmethod
    def mkdirs(cls):
        run("mkdir -p %s" % cls.deploy_dir)
        run("mkdir -p %s/releases" % cls.deploy_dir)
        run("mkdir -p %s" % cls.share_dir)
        run("mkdir -p %s/run" % cls.share_dir)
        run("mkdir -p %s/static" % cls.share_dir)
        run("mkdir -p %s/media" % cls.share_dir)
        run("mkdir -p %s/bower_components" % cls.share_dir)
        run("mkdir -p %s/components" % cls.share_dir)
        run("mkdir -p %s/node_modules" % cls.share_dir)
        run("mkdir -p %s/media/uploads" % cls.share_dir)
        run("mkdir -p %s/media/uploads/ckeditor" % cls.share_dir)
        run("mkdir -p %s" % cls.program_dir)
        run("mkdir -p -m 777 /var/log/journeytech.vn")
        run("touch %s" % cls.current_dir)  # so that we can remote it later
        run("touch %s/local_settings.py" % cls.share_dir)

    @classmethod
    def remove_old_versions(cls):
        run("cd %s; ls -lt | tail -n +10 | xargs rm -rf;" % cls.release_dir)

    @classmethod
    def checkout_source(cls, current_time):
        cls.release_dir = "%s/releases/%s" % (cls.deploy_dir, current_time)
        run("git clone %s %s;" % (cls.git_source, cls.release_dir))

        run("cd %s; git checkout %s" % (cls.release_dir, cls.branch()))
        run("chown -R www-data:www-data %s" % cls.release_dir)

        cls.run("ln -s %s/media %s/media" % (cls.share_dir, cls.release_dir))
        cls.run("ln -s %s/static %s/static" % (cls.share_dir, cls.release_dir))

        cls.run("ln -s %s/local_settings.py %s/local_settings.py" % (cls.share_dir, cls.release_dir))

        cls.run("rm -f %s" % cls.bin_dir)
        cls.run("ln -s %s/bin %s" % (cls.release_dir, cls.bin_dir))
        cls.run("ln -s %s/components %s/components" % (cls.share_dir, cls.release_dir))
        cls.run("ln -s %s/bower_components %s/bower_components" % (cls.share_dir, cls.release_dir))
        cls.run("ln -s %s %s/env" % (cls.virtualenv_dir, cls.release_dir))
        cls.run("ln -s %s %s/program" % (cls.program_dir, cls.release_dir))
        cls.run("ln -s %s %s/log" % (cls.log_dir, cls.release_dir))

    @classmethod
    def run_virtualenv(cls, command):
        cls.run("source %s/bin/activate; %s" % (cls.virtualenv_dir, command))

    @classmethod
    def install_requirements(cls):
        cls.run_virtualenv("cd %s; pip install -r requirements.txt --allow-all-external --allow-unverified PIL" % cls.release_dir)

    @classmethod
    def get_python_version(cls):
        if cls.is_command_exists("python"):
            return run("python -V").split(' ')[1]
        return ""

    @classmethod
    def install_python(cls):
        cls.python_path = cls.get_command_real_path("python")
        cls.install_setup_tools()
        cls.install_pip()
        cls.install_virtualenv()
        cls.easy_install_path = cls.get_command_real_path("easy_install")
        cls.pip_path = cls.get_command_real_path("pip")
        cls.virtualenv_path = cls.get_command_real_path("virtualenv")

    @classmethod
    def install_setup_tools(cls):
        if not cls.is_command_exists('easy_install'):
            run("cd ~; wget https://pypi.python.org/packages/source/s/setuptools/setuptools-1.1.5.tar.gz --no-check-certificate")
            run("cd ~; tar -xf setuptools-1.1.5.tar.gz")
            run("python2.7 ~/setuptools-1.1.5/setup.py install")

    @classmethod
    def install_redis(cls):
        if not cls.is_command_exists('redis-cli'):
            if cls.have_yum:
                run("yum install redis -y")
            else:
                run("apt-get install redis-server -y")

    @classmethod
    def install_pip(cls):
        if not cls.is_command_exists('pip'):
            run("%s pip" % cls.get_command_real_path('easy_install'))

    @classmethod
    def install_virtualenv(cls):
        if not cls.is_command_exists('virtualenv'):
            run("%s install virtualenv" % cls.get_command_real_path('pip'))

    @classmethod
    def is_file_exists(cls, filename):
        return run("if test -f %s; then echo 1; else echo 0; fi" % filename) == '1'

    @classmethod
    def create_virtualenv(cls):
        if not cls.is_file_exists('%s/bin/activate' % cls.virtualenv_dir) :
            cls.run("%s %s" % (cls.virtualenv_path, cls.virtualenv_dir))

    @classmethod
    def install_mysql_dev(cls):
        if cls.have_yum:
            run("yum install mysql-devel -y")
        else:
            run("apt-get install libmysqld-dev -y")

    @classmethod
    def create_user_and_group(cls):
        # user not exists
        try:
            run("useradd www-data")
        except:
            if not run("cat /etc/group | grep www-data"):
                run("groupadd www-data")
                run("useradd -G www-data www-data")

    @classmethod
    def chown_dirs(cls):
        run("chown -R www-data:www-data %s" % cls.deploy_dir)
        run("chown -R www-data:www-data %s" % cls.deploy_dir)

    @classmethod
    def install_supervisor(cls):
        if not cls.is_command_exists('supervisorctl'):
            if cls.have_yum:
                run("yum install supervisor -y")
            else:
                run("apt-get install supervisor -y")

    @classmethod
    def copy_system_config_files(cls):
        run("rm -f /etc/nginx/sites-enabled/journeytech.vn.conf")
        run("cp %s/bin/nginx.conf /etc/nginx/sites-enabled/journeytech.vn.conf" % cls.release_dir)

    @classmethod
    def restart_web_services(cls):

        run("chmod 777 %s/bin/*.sh" % cls.current_dir)

        cls.run_virtualenv("supervisorctl -c%s/bin/supervisor.conf shutdown" % cls.current_dir)
        cls.run_virtualenv("supervisord -c%s/bin/supervisor.conf" % cls.current_dir)

        run("service nginx restart")

    @classmethod
    def run_migration(cls):
        cls.run_virtualenv('cd %s; python manage.py migrate' % cls.release_dir)
        cls.run_virtualenv('cd %s; python manage.py update_permissions;' % cls.release_dir)

    @classmethod
    def collect_statics(cls):
        cls.run_virtualenv("cd %s; python manage.py collectstatic --noinput" % cls.release_dir)

    @classmethod
    def install_bower_component(cls):
        cls.run_virtualenv("cd %s; python manage.py bower_install -- --allow-root" % cls.release_dir)

    @classmethod
    def collect_current_statics(cls):
        cls.run_virtualenv("cd %s; python manage.py collectstatic --noinput" % cls.current_dir)

    @classmethod
    def install_image_libs(cls):
        if cls.have_yum:
            run("yum install libpng-devel -y")
            run("yum install libjpeg-devel -y")
        else:
            run("apt-get install libpng-devel -y")
            run("apt-get install libjpeg-devel -y")

    @classmethod
    def combine_django_messages(cls):
        cls.run_virtualenv("cd %s; python manage.py compilemessages" % cls.release_dir)

    @classmethod
    def install_kindlegen(cls):
        if not cls.is_file_exists("%s/kindlegen" % cls.program_dir):
            run("cd /tmp; wget http://kindlegen.s3.amazonaws.com/kindlegen_linux_2.6_i386_v2_9.tar.gz")
            run("cd /tmp; tar -xf kindlegen_linux_2.6_i386_v2_9.tar.gz")
            run("cp /tmp/kindlegen %s" % cls.program_dir)

    @classmethod
    def branch(cls):
        return local("git branch | grep \"*\"", capture=True)[2:]

    @classmethod
    def update_cronjob_files(cls):
        replacements = {
            'virtualenv_dir': cls.virtualenv_dir,
            'release_dir': cls.release_dir,
            'share_dir': cls.share_dir,
            'bin_dir': cls.bin_dir,
            'program_dir': cls.program_dir,
            'log_dir': cls.log_dir,
            'current_dir': cls.current_dir
        }
        dirs = os.listdir(".")
        sub_dirs = ('cron.daily', 'cron.hourly', 'cron.monthly', 'cron.weekly', 'cron.d',)
        for sub_dir in sub_dirs:
            cron_dir = os.path.join('/', 'etc', sub_dir)
            run("rm -f %s/%s*" % (cron_dir, cls.project_name))
        for dir_name in dirs:
            if not os.path.isdir(dir_name):  # if not a folder
                continue

            cronjobs_dir = "%s/cronjobs" % dir_name
            if not os.path.isdir(cronjobs_dir):  # if no crontabs
                continue
            for sub_dir in sub_dirs:
                cron_dir = "%s/%s" % (cronjobs_dir, sub_dir)
                if not os.path.isdir(cron_dir):
                    continue
                cron_files = os.listdir(cron_dir)
                for cron_file in cron_files:
                    source_file = os.path.join(cls.release_dir, dir_name, "cronjobs", sub_dir, cron_file)
                    destination_file_name = "%s_%s_%s" % (cls.project_name, dir_name, cron_file)
                    destination_file = os.path.join('/', 'etc', sub_dir, destination_file_name)
                    command = "cat %s" % source_file
                    for key, value in replacements.items():
                        command += " | sed 's/{{%s}}/%s/g'" % (key, value.replace('/', '\/'))
                    command += " > %s" % destination_file
                    run(command)

                    run("chmod 777 %s" % destination_file)

    @classmethod
    def install_socket_io(cls):
        if not cls.is_command_exists("npm"):
            run("cd /tmp; wget http://nodejs.org/dist/v0.10.22/node-v0.10.22.tar.gz")
            run("cd /tmp; tar -xf node-v0.10.22.tar.gz")
            run("cd /tmp/node-v0.10.22; ./configure")
            run("cd /tmp/node-v0.10.22; make")
            run("cd /tmp/node-v0.10.22; make install")
            path = run("whereis npm").split(" ")[1]
            run("%s install socket.io" % path)
            run("%s install express" % path)

    @classmethod
    def install_node_modules(cls):
        packages = cls.run("cat %s/socket.io/requirements.txt" % cls.release_dir).split("\n")
        for package in packages:
            cls.run("cd %s; npm install %s" % (cls.share_dir, package))
        cls.run("ln -s %s/node_modules %s/node_modules" % (cls.share_dir, cls.release_dir))

    @classmethod
    def install_bower(cls):
        cls.run("npm install -g bower")

    @classmethod
    def setup(cls):
        cls.init()
        cls.mkdirs()
        cls.install_git()
        cls.install_python()
        cls.create_user_and_group()
        cls.chown_dirs()
        cls.create_virtualenv()
        cls.install_mysql_dev()
        cls.install_supervisor()
        cls.install_bower()

    @classmethod
    def update_file_path(cls):
        run("rm %s" % cls.current_dir)
        run("ln -s %s %s" % (cls.release_dir, cls.current_dir))

    @classmethod
    def deploy(cls):
        cls.setup()
        current_time = run("date +%Y%m%d%H%M%S")
        cls.checkout_source(current_time)
        cls.install_requirements()
        cls.run_migration()
        cls.install_bower_component()
        cls.collect_statics()
        # cls.combine_django_messages()
        cls.copy_system_config_files()
        # cls.update_cronjob_files()
        cls.update_file_path()
        cls.restart_web_services()

    @classmethod
    def init_folder_tree(cls):
        local("mkdir -p run")
        local("mkdir -p static")
        local("mkdir -p log")
        local("mkdir -p media")
        local("python manage.py syncdb --migrate")


    @classmethod
    def update_local(cls):
        cls.init_folder_tree()
        local("cd program; curl -O http://kindlegen.s3.amazonaws.com/kindlegen_linux_2.6_i386_v2_9.tar.gz")
        local("cd program; tar -xf kindlegen_linux_2.6_i386_v2_9.tar.gz")
        local("run mkdir -p /var/log/journeytech.vn/")
        local("run chmod 777 /var/log/journeytech.vn/")
        local("run apt-get install libjpeg-dev -y")
        local("run apt-get install libpng-dev -y")
        local("git pull origin %s" % cls.branch())
        local("pip install -r requirements.txt")
        local("python manage.py syncdb --migrate")
