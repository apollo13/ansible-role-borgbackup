#!/usr/bin/python

DOCUMENTATION = """
---
module: borgbase
author: "Philipp Rintz (https://github.com/p-rintz)"
short_description: Ansible module for creating new repositories with borgbase.com
description:
  - Ansible Module for creating new repositories with borgbase.com including adding new ssh keys
version_added: "2.6"
"""

EXAMPLES = """
- name: Create new repository for server in EU with new SSH_key and quota
  borgbase:
    repository_name: "{{ inventory_hostname }}"
    token: "Your Borgbase API Token"
    new_ssh_key: True
    ssh_key: "{{ some_variable }}"
    append_only: True
    quota_enable: True
    quota: 1000 #in GB
    region: eu
    alertdays: 2
  delegate_to: localhost
- name: Create new repository without new key and no quota/alerting in US region
  borgbase:
    repository_name: "{{ inventory_hostname }}"
    token: "Your Borgbase API Token"
    new_ssh_key: False
    ssh_key: "ssh-ed25519 AAAAC3Nz......aLqRJw+dl/E+2BJ xxx@yyy"
    region: us
  delegate_to: localhost
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.borgbase_api_client.client import GraphQLClient
from ansible.module_utils.borgbase_api_client.mutations import SSH_ADD
from ansible.module_utils.borgbase_api_client.queries import KEY_DETAILS


REPO_ADD = """
mutation repoAdd(
  $name: String
  $quota: Int
  $quotaEnabled: Boolean
  $appendOnlyKeys: [String]
  $fullAccessKeys: [String]
  $alertDays: Int
  $region: String
  $borgVersion: String
  ) {
    repoAdd(
      name: $name
      quota: $quota
      quotaEnabled: $quotaEnabled
      appendOnlyKeys: $appendOnlyKeys
      fullAccessKeys: $fullAccessKeys
      alertDays: $alertDays
      region: $region
      borgVersion: $borgVersion
    ) {
      repoAdded {
        id
        name
        repoPath
      }
    }
}
"""

REPO_DETAILS = """
query repoList {
  repoList {
    id
    name
    repoPath
  }
}
"""


def get_or_create_ssh_key(client, module):
    id = module.params["ssh_key"]
    res = client.execute(KEY_DETAILS)
    for i in res["data"]["sshList"]:
        if i["keyData"] == id:
            return i["id"], False

    key_name = "Key for %s" % (module.params["repository_name"],)
    new_key_vars = {"name": key_name, "keyData": module.params["ssh_key"]}
    res = client.execute(SSH_ADD, new_key_vars)
    new_key_id = res["data"]["sshAdd"]["keyAdded"]["id"]
    return new_key_id, True


def get_or_create_repo(client, module, ssh_id):
    name = module.params["repository_name"]
    res = client.execute(REPO_DETAILS)
    for i in res["data"]["repoList"]:
        if i["name"] == name:
            return i, False

    if module.params["append_only"]:
        access_level = "appendOnlyKeys"
    else:
        access_level = "fullAccessKeys"

    new_repo_vars = {
        "name": module.params["repository_name"],
        "quotaEnabled": module.params["quota_enable"],
        access_level: [ssh_id],
        "alertDays": module.params["alertdays"],
        "region": module.params["region"],
    }
    if module.params["quota_enable"]:
        new_repo_vars["quota"] = 1000 * module.params["quota"]

    res = client.execute(REPO_ADD, new_repo_vars)
    return res["data"]["repoAdd"]["repoAdded"], True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            repository_name=dict(type="str", required=True,),
            token=dict(required=True, type="str", no_log=True),
            # new_ssh_key=dict(required=False, default="True", type="bool"),
            ssh_key=dict(required=True, type="str"),
            append_only=dict(required=False, default="True", type="bool"),
            quota_enable=dict(required=False, default="False", type="bool"),
            quota=dict(required=False, type="int"),
            region=dict(required=True, type="str", choice=["eu", "us"]),
            alertdays=dict(required=False, default=0, type="int"),
        )
    )

    client = GraphQLClient(module.params["token"])

    # Setup information for Ansible
    result = dict(changed=False, data="", type="")

    try:
        # Add new SSH key or get ID of old key
        key_id, changed = get_or_create_ssh_key(client, module)

        # Add new repo using the key
        repo, changed = get_or_create_repo(client, module, key_id)

        # Test for success and change info
        result["changed"] = changed
        result["data"] = repo
    except Exception:
        module.fail_json(msg="Failed creating new respository.", **result)
    else:
        module.exit_json(**result)


if __name__ == "__main__":
    main()
