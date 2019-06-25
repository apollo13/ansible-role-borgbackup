testinfra_hosts = ["borg-centos-upstream", "borg-centos-system"]


def test_backup(host):
    assert host.run("systemctl start borgbackup").rc == 0
    assert host.run("systemctl is-failed borgbackup").rc == 1
    assert host.run("systemctl is-failed 'borgbackup@*'").rc == 1
