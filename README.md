# Borgbackup Ansible Role

This role aims to implement a fully managed `borg` setup. The feature list currently includes:

 * Client & server configuration, whereas each client gets their own repository.
 * Support for automatically creating repositories on borgbase.com.
 * Backups happens as unprivileged user.
 * Automatic configuration of `known_hosts` so even initial connections are a success.
 * Initialization of the repository on the clients.
 * Optional `append-only` mode as well as management configuration for admin access.
 * Scheduled via `systemd timers`.
 * The config (currently, PRs welcome) uses `repokey-blake2` and backs up using `--compression lz4`.

Other roles can optionally add the following configurations (see examples below):

 * Extra directories to add to the backup.
 * Backup tasks (think of creating a database dump) before the actual backup via arbritrary users.

## Role variables

### Common variables

The role allows installation via the OS package manager (default) as well as directly from upstream (via Github releases):

```
borgbackup_install_method: system|upstream
```
If upstream is chosen, one needs to specify version and checksum (defaults to version `1.1.10`):
```
borgbackup_upstream_version: 1.1.10
borgbackup_upstream_checksum: sha256:6338d67aad4b5cd327b25ea363e30f0ed4abc425ce2d6a597c75a67a876ef9af
```
If needed the backup user can be specified:
```
borgbackup_user: borg
```
For client machines, this is the user executing borgbackup and for server machines this is the user that runs `borg serve` when the client connects to it over SSH.

**Attention:** This role does not create the user you choose; this has to be done manually before being able to use this role. For instance:
```
- name: Create user for borgbackup
  user:
    name: "{{ borgbackup_user }}"
    state: present
```

### Client variables

At a minimum it is required to set backup directories as well as a passphrase per client:
```
borgbackup_passphrase: XXX_SECRET_XXX
borgbackup_directories: ["{{ borgbackup_home }}/data"] # default
```

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
borgbackup_hostkey_checking: ask/off/accept-new # (Matches SSH's StrictHostKeyChecking, defaults to ask)
```
Note that the default of `borgbackup_hostkey_checking` is set to `ask` to ensure that host keys are verified, ie configured via `borgbackup_known_hosts`.
Alternatively one can set it to `accept-new` to activate a "trust on first use" behavior.

The following example shows how to configure extra options:
```
borgbackup_calendar_spec: "*-*-* 2:00:00" # default, pattern is in systemd-timer format and describes when to run borgbackup
borgbackup_exclude_patterns: [] # default, see borg help patterns, uses fnmatch-style format
borgbackup_append_only: yes # default, matches the borg append-only behavior
borgbackup_use_cap_dac_read_search: no # default
```

**Attention:** It is recommended to either use `root` or a dedicated backup user (the role defaults to using `borg`). Since the unprivileged `borg` user could only read it's own files, `borgbackup_use_cap_dac_read_search` can be set to use `yes` which will give the running users the permission to read all files when executed via the systemd-timer.

### Support for borgbase.com

To enable support for borgbase.com the following variables need to be defined:
```
borgbackup_bb_repo: borgbase repository name
borgbackup_bb_apikey: borgbase api key
borgbackup_hostkey_checking: accept-new # Otherwise host-key checking will fail since we don't know the host-key
                                        # Alternatively connect manually via ssh after running the playbook and accept the hostkey
```
Once those are set `borgbackup_repository` will be defined automatically. Be aware that this role only _creates_ the repo and key on borgbase.com, it will never modify an existing repository. This means that you can (and should) use a limited API-Token with _Create Only_ permission. It also means that you need one repository per server, which is good to prevent locking conflicts anyways.

Furthermore the creation of the borgbase repository can be controlled via:
```
borgbackup_bb_quota: 1000 # in GB (defaults to undefined resulting in no quota)
borgbackup_bb_region: eu/us (defaults to eu)
borgbackup_bb_alertdays: 1 (defaults to undefined leading to no alerts)
```

### Server variables

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

## Registration of extra backup folders as well as pre-backup tasks/programs

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

## Backup status & monitoring

Since everything is executed via systemd, the status can be checked easily via monitoring systems. The relevant unit are:

 * `borgbackup.service` the actual run of `borgbackup`.
 * `borgbackup-tasks.service` as placeholder that collects the exit status of the pre backup programs.
 * `borgbackup-tasks@<task_name.service>` Individual backup tasks as registered in the example above.
