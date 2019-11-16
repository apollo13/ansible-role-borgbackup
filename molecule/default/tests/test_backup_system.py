testinfra_hosts = ["borg-system"]


def test_system_borg_installed(host):
    assert host.package("borgbackup").is_installed


def test_backup(host):
    result = host.run("systemctl --wait start borgbackup")
    if result.rc == 1 and "unrecognized option" in result.stderr:
        result = host.run("systemctl start borgbackup")
    assert result.rc == 0
    # Note: is-failed returns 0 if a service failed
    assert host.run("systemctl is-failed borgbackup").rc == 1
    # System-Borg was configured to succeed in playbook.yml
    assert host.run("systemctl is-failed borgbackup-tasks").rc == 1
