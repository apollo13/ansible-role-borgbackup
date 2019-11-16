testinfra_hosts = ["borg-srv-ubuntu"]


def test_upstream_borg_installed(host):
    assert not host.package("borgbackup").is_installed
    assert host.file("/usr/local/bin/borg").is_file
    print(host.ansible.get_variables())
    cmd = host.run("/usr/local/bin/borg --version")
    assert cmd.stdout.strip() == "borg 1.1.10"


def test_borg_backup_storage(host):
    storage = host.file("/var/borg")
    assert storage.exists
    assert storage.is_directory
    assert storage.user == "test"
