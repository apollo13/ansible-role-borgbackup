testinfra_hosts = ["borg-ubuntu-upstream", "borg-ubuntu-system"]


def test_backup(host):
    # Note: is-failed returns 0 if a service failed
    assert host.run("systemctl --wait start borgbackup").rc == 0
    assert host.run("systemctl is-failed borgbackup").rc == 1
    assert host.run("systemctl is-failed borgbackup-tasks").rc == 0
