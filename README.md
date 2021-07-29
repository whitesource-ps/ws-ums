![Logo](https://whitesource-resources.s3.amazonaws.com/ws-sig-images/Whitesource_Logo_178x44.png)  

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)]
[![GitHub release](https://img.shields.io/github/v/release/whitesource-ps/ws-ums)](https://github.com/whitesource-ps/ws-ums/releases/latest)  
[![GitHub package](https://img.shields.io/github/package-json/v/whitesource-ps/ws-ums)](https://github.com/whitesource-ps/ws-ums/pkgs/container/ws-ums)

# WhiteSource IAM User Management
API Service to perform users operations on large scale environment (Global Organizations).
The service supports 2 actions:
1. Create and assign users to products with multi-organization setup.
    1. Create user in the organization.
    1. Create group with the role name in the organization.
    1. Assign user to the designated group
    1. Assign group to given product(s)
    
    Call: **/createAndAssignUser**
    ```http request 
    {
      "userName": "userName", 
      "userEmail": "userEmail",
      "ghOrgNames": [ghOrgName1, ghOrgName2, …],
      "wsRole": "ws_role" 
    }
    ```

1. Delete users from multi organizations
   Call: **/deleteUser**
    ```http request 
    {
      "userEmail": "user_mail",
      "ghOrgNames": [gh_org_name_1, gh_org_name_2, … ],
    }
    ```

## Prerequisites
* Provided user key must be defined as Global admin and admin on all organizations

## Installation
Download and deploy Docker image:
```shell
docker pull whitesourcetools/ws-ums
docker run --name ws-ums -p 8432:8432 -e WS_USER_KEY=<WS_USER_KEY> -e WS_GLOBAL_TOKEN=<WS_GLOBAL_TOKEN> -e WS_URL=<WS_URL> \
-e WS_INVITER=<WS_INVITER> -v /<PATH>:/tmp whitesourcetools/ws-ums
```


