testinfra_hosts = ["borg-srv"]


def test_borg_backup_storage(host):
    storage = host.file("/var/borg")
    assert storage.exists
    assert storage.is_directory
    assert storage.user == "borg"


def test_management_access(host):
    data = host.file("/home/borg/.ssh/authorized_keys").content_string
    for line in data.splitlines():
        if line.strip().endswith("adminuser"):
            assert (
                "cd /var/borg; /usr/bin/borg serve --restrict-to-path /var/borg" in line
            )
            break
    else:
        assert False, "adminuser not in authorized_keys"
