## 4.0.0 (2024-01-01)

 - INCOMPATIBLE: Switch default upstream binaries to linuxnew64. They don't work on CentOS 7 and other
   old systems. One can still adjust `borgbackup_upstream_url`/`borgbackup_upstream_checksum` accordingly.
 - Updated default borg version to 1.2.7.

## 3.0.6 (2024-01-01)

 - Disable SSH passwort authentication to prevent hanging if the ssh keyfile is not found.
 - Added support for `OnFailure` in systemd services.

## 3.0.5 (2021-03-14)

 - Updated default borg version to 1.1.15.

## 3.0.4 (2020-07-31)

- Added support for rate limiting uploads via `borgbackup_remote_ratelimit`.

## 3.0.3 (2020-07-29)

- Wait 10 seconds for DNS to propagate after creating a borgbase repository.

## 3.0.2 (2020-04-23)

- Made `backup_user` and `paths` actually optional when used from `configure.yml`.

## 3.0.1 (2020-04-23)

- Updated default borg version to 1.1.11.

## 3.0.0 (2020-02-22)

- INCOMPATIBLE: Requires at least ansible 2.9 due to the usage of a new throttle keyword.

## 2.0.0 (2020-01-28)

- INCOMPATIBLE: Disabled `DAC_READ_SEARCH` cap by default, use `borgbackup_use_cap_dac_read_search` to reenable.

## 1.0.0 (2020-01-05)

- INCOMPATIBLE: Requires at least ansible 2.8 due to the usage of a new module.
- Added support for Travis CI.
- Added support for exclude patterns.

## 0.2.2 (2019-11-16)

- Fixed key naming on borgbase.com and updated docs.

## 0.2.1 (2019-11-16)

- Added testing against Centos 8 and Ubuntu 19.10.
- Fixed Ansible Galaxy integration.

## 0.2.0 (2019-11-16)

- Added support for borgbase.com.
- Removed the creation of the borg user and created custom SSH keys.

## 0.1.0 (2019-06-27)

- Initial version.
