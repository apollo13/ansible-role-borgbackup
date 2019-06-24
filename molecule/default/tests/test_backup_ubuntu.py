testinfra_hosts = ["borg-ubuntu-upstream", "borg-ubuntu-system"]


def test_backup(host):
    assert host.run("systemctl --wait start borgbackup").rc == 0
    assert host.run("systemctl is-failed borgbackup").rc == 1
