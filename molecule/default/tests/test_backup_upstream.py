testinfra_hosts = ["borg-upstream"]


def test_upstream_borg_installed(host):
    assert not host.package("borgbackup").is_installed
    assert host.file("/usr/local/bin/borg").is_file
    cmd = host.run("/usr/local/bin/borg --version")
    assert cmd.stdout.strip() == "borg 1.1.15"


def test_backup(host):
    result = host.run("systemctl --wait start borgbackup")
    if result.rc == 1 and "unrecognized option" in result.stderr:
        result = host.run("systemctl start borgbackup")
    assert result.rc == 0
    # Note: is-failed returns 0 if a service failed
    assert host.run("systemctl is-failed borgbackup").rc == 1
    # Upstream-Borg was configured to fail in playbook.yml
    assert host.run("systemctl is-failed borgbackup-tasks").rc == 0
