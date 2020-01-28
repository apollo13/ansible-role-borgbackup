## 2.0.0 (2020-01-28)

- INCOMPATIBLE: Disabled DAC_READ_SEARCH cap by default, use borgbackup_use_cap_dac_read_search to reenable.

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
