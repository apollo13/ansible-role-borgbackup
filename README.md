## Borgbackup Ansible Role

This role aims to implement a fully managed `borg` setup. The feature list currently includes:

 * Client & server configuration, whereas each client gets their own repository.
 * Backups happens as unprivileged user.
 * Automatic configuration of `known_hosts` so even initial connections are a success.
 * Initialization of the repository on the clients.
 * Optional `append-only` mode as well as management configuration for admin access.
 * Scheduled via `systemd timers`.
 * The config (currently, PRs welcome) uses `repokey-blake2` and backs up using `--compression lz4`.

Other roles can optionally add the following configurations (see examples below):

 * Extra directories to add to the backup.
 * Backup tasks (think of creating a database dump) before the actual backup via arbritrary users.

### Role variables

#### Common variables

The role allows installation via the OS package manager (default) as well as directly from upstream (via Github releases):

```
borgbackup_install_method: system|upstream
```
If upstream is chosen, one needs to specify version and checksum (defaults to version `1.1.10`):
```
borgbackup_upstream_version: 1.1.10
borgbackup_upstream_checksum: sha256:6338d67aad4b5cd327b25ea363e30f0ed4abc425ce2d6a597c75a67a876ef9af
```
If needed the backup user and home directory can be specified (defaults are as shown below):
```
borgbackup_user: backup
borgbackup_home: "/home/{{ borgbackup_user }}/borg"
```

#### Client variables

If the server is managed by ansible, the repository can be configured by specifying
```
borgbackup_repository_server: some_inventory_hostname
```
and the role will do it's magic behind the scenes to automatically configure the server for access as well as initialize a repository.

In cases where the server is managed outside of ansible, one needs to configure the actual backup repository as well as host keys of the server:
```
borgbackup_repository: ssh://test@borgbackup.cloud/~/storage
borgbackup_known_hosts:
  - "borgbackup.cloud ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIElvcKplWycItag/MP7gYUCy95WIhMM1OFKbZ/j/ykFE"
```

The following example shows how to configure passphrase, schedule times and backup directories:
```
borgbackup_passphrase: XXX_SECRET_XXX
borgbackup_calendar_spec: "*-*-* 2:00:00" # default
borgbackup_directories: ["{{ borgbackup_home }}/data"] # default
borgbackup_append_only: yes # default
```

#### Server variables

The server configuration is rather boring, it allows to specify a storage root via
```
borgbackup_repository_storage: /some/path
```
and is currently required to "trigger" the server behavior of this role.

If client use `borgbackup_append_only` one can configure the server to allow a special admin key(s) to access all repositories:
```
borgbackup_management_keys:
  - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIElvcKplWycItag/MP7gYUCy95WIhMM1OFKbZ/j/ykFE adminuser"
```

### Registration of extra backup folders as well as pre-backup tasks/programs

The role is written in a way that it can be extended dynamically from other roles. The only requirement is that the `apollo13.borgbackup` role is run once before other roles can extend it.

To extend the backup functionality from a fictional `postgresql` role one could do the following (inside of `tasks/main.yml` of the `postgresql` role):
```
include_role:
  name: apollo13.borgbackup
  tasks_from: configure.yml
vars:
  service: postgresql_dump # Needs to be unique between all the services on a host
  backup_user: postgresql # Optional, the user to execute the backup command under
  # The backup command is used in a systemd unit, so use sh if redirection is required
  backup_command: /bin/sh -c "pg_dumpall > /var/lib/postgresql/backup/db.out"
  # Extra path to add to the backup
  paths:
    - /var/lib/postgresql/backup/
```

The above example configures an extra systemd unit that runs before the backup to execute `pg_dumpall` as `postgresql` and adds `/var/lib/postgresql/backup/` to the path to backup.

### Backup status & monitoring

Since everything is executed via systemd, the status can be checked easily via monitoring systems. The relevant unit are:

 * `borgbackup.service` the actual run of `borgbackup`.
 * `borgbackup-tasks.service` as placeholder that collects the exit status of the pre backup programs.
 * `borgbackup-tasks@<task_name.service>` Individual backup tasks as registered in the example above.
