# Setting up a server with the ansible playbook

## Description

### Overview of the services running

* A front-facing nginx server (port 80) forwarding to the hypha django app (see next)
* A docker container running the torchbox/wtsh-hypha image and managed via a systemd unit
* A docker container running the database (postgres 16) and managed via a systemd unit


### Ansible roles

The code is organised by roles, with the main playbook (`setup.yml`) depending on all of them.

* `system` sets up basic system configuration like timezone or important packages
* `docker` installs docker following the guide at https://docs.docker.com/engine/install/debian/#install-using-the-repository
* `nginx` installs the `nginx` package from Debian's repository
* `hypha` configures a systemd service that runs our `torchbox/wtsh-hypha` image (and a postgres 16 image for its database)


## Creating a VM for local testing with Vagrant

If you have `vagrant` installed (and probably `virtualbox` too), then you should be able to create a VM with:
```
vagrant up
```
(this assumes you're inside the `ansible` directory, aka the one that contains this README)


## Running the ansible playbook

### The inventory file

First create an `inventory.ini` file with a single line containing the IP address (or the domain name) of the server.

If needed, you can also specify a port number:
```
198.51.100.0:2222
```

When using the local Vagrant setup, you also want to change the `ansible_user` and `ansible_ssh_private_key_file`:
```
wtsh-hypha.localhost:2222 ansible_user=vagrant ansible_ssh_private_key_file=.vagrant/machines/default/virtualbox/private_key
```
(I used the `wtsh-hypha.localhost` domain here which should automatically resolve to `localhost` without any configuration, if that's not the case you can set up something in `/etc/hosts` or use `127.0.0.1` or `localhost` as the domain)

### The secrets file

Secrets that should not appear in public source code (like `SECRET_KEY` or various passwords and API keys) should go in a `/srv/hypha/hypha.env` file on the server. This playbook will only create this file if it's missing (with some default values). If you need to make changes to it later on, you must edit the file by hand directly on the server.


### Running the playbook

Once the `inventory.ini` file is created, setting up the server should be as easy as:
```
uvx --from ansible ansible-playbook -i inventory.ini setup.yml
```
(that's assuming you have uv installed, otherwise you'll have to install `ansible` manually, probably via `pip` + `virtualenv`)
