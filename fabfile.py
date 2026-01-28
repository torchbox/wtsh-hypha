import json
import os
import subprocess
import sys
from shlex import quote

from invoke import run as local
from invoke.context import Context
from invoke.tasks import task

LOCAL_DATABASE_NAME = "hypha"


#############
# Development
#############


def dexec(cmd, service="web"):
    return local(
        "docker compose exec -T {} bash -c {}".format(quote(service), quote(cmd))
    )


@task
def build(c: Context):
    """
    Build the development environment (call this first)
    """
    # Check if the web container is running, fail and prompt the user to stop it
    # first if so.
    web_status_json = subprocess.check_output(
        ["docker", "compose", "ps", "--all", "--format=json", "web"],
        encoding="utf-8",
    )
    if json.loads(web_status_json or "{}").get("State") == "running":
        print(
            "The web container is currently running. "
            "Please stop it with `fab stop` before running this task."
        )
        sys.exit(1)

    # Remove the web container, if it exists. If we don't do this, we won't be
    # able to drop the node_modules volume below, so just exit with an error.
    subprocess.check_call(["docker", "compose", "rm", "--force", "web"])

    # If the node_modules named volume exists, try to remove it so that it
    # gets reinitialised with the node_modules/ from the image. This guarantees
    # that the Node dependencies are up to date after running this task.
    web_service_config_json = subprocess.check_output(
        ["docker", "compose", "config", "--format=json", "web"],
        encoding="utf-8",
    )
    web_service_config = json.loads(web_service_config_json)
    node_modules_volume_name = web_service_config["volumes"]["node_modules"]["name"]
    subprocess.run(["docker", "volume", "rm", "--force", node_modules_volume_name])

    # Pull up-to-date images and build the development environment
    local("docker compose pull")
    local(
        f"docker compose build --build-arg UID={os.getuid()} --build-arg GID={os.getgid()}"
    )


@task
def start(c):
    """
    Start the development environment
    """
    local("docker compose up --detach")


@task
def stop(c):
    """
    Stop the development environment
    """
    local("docker compose stop")


@task
def restart(c):
    """
    Restart the development environment
    """
    stop(c)
    start(c)


@task
def destroy(c):
    """
    Destroy development environment containers and volumes (database will be lost!)
    """
    local("docker compose down --volumes")


@task
def sh(c, service="web"):
    """
    Run bash in a local container
    """
    subprocess.run(["docker", "compose", "exec", service, "bash"])


@task
def delete_docker_database(c):
    dexec("psql -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'")


@task(
    help={
        "new_default_site_hostname": "Pass an empty string to skip the default site's hostname replacement"
        " - default is 'localhost:8000'"
    }
)
def import_data(
    c, database_filename: str, new_default_site_hostname: str = "localhost:8000"
):
    """
    Import local data file to the db container.
    """
    delete_docker_database(c)
    dexec(
        f"pg_restore --clean --if-exists --no-owner --no-acl --dbname={LOCAL_DATABASE_NAME} {database_filename}",
    )

    # When pulling data from a heroku environment, the hostname in wagtail > sites is not updated.
    # This means when browsing the site locally with this pulled data you can end up with links to staging, or even
    # the live site.
    # --> let's update the default site hostname values
    if new_default_site_hostname:
        if ":" in new_default_site_hostname:
            hostname, port = new_default_site_hostname.split(":")
        else:
            hostname, port = new_default_site_hostname, "8000"
        assert hostname and port and port.isdigit()
        dexec(
            f"psql -c \"UPDATE wagtailcore_site SET hostname = '{hostname}', port = {port} WHERE is_default_site IS TRUE;\""  # noqa: E501
        )
        print(f"Default site's hostname was updated to '{hostname}:{port}'.")

    print(
        "Any superuser accounts you previously created locally will have been wiped and will need to be recreated."
    )


#######
# Utils
#######


def make_bold(msg):
    return "\033[1m{}\033[0m".format(msg)


@task
def docker_coverage(c):
    return dexec(
        "coverage erase && coverage run manage.py test \
            --settings=hypha.settings.test && coverage report",
    )


@task
def run_test(c):
    """
    Run python tests in the web container
    """
    subprocess.call(
        [
            "docker",
            "compose",
            "exec",
            "web",
            "python",
            "manage.py",
            "test",
            "--settings=hypha.settings.test",
            "--parallel",
        ]
    )
