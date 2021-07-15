import json
import logging
import os
import sys
import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
from ws_sdk.web import WS
from ws_sdk import ws_constants, ws_utilities

LOG_LEVEL = logging.DEBUG if os.environ.get("DEBUG", logging.INFO) else logging.INFO
logging.getLogger('urllib3').setLevel(logging.INFO)
logging.basicConfig(level=LOG_LEVEL, stream=sys.stdout)

with open("config.json", 'r') as f:
    config = json.loads(f.read())
config['ws_url'] = os.environ.get('WS_URL')
config['ws_user_key'] = os.environ.get('WS_USER_KEY')
config['ws_global_token'] = os.environ.get('WS_GLOBAL_TOKEN')
config['ws_conn_global'] = WS(url=os.environ.get('ws_url'),
                              user_key=os.environ.get('ws_user_key'),
                              token=os.environ.get('ws_global_token'),
                              token_type=ws_constants.GLOBAL)

api = FastAPI(title="WS_IAM_UM",  swagger_static={"favicon": "favicon.png"})


def convert_gh_orgs_to_ws_prods(gh_org_names) -> list:
    """
    convert a list of GitHub Organization into WhiteSource Products
    :param gh_org_names: list of GH Organizations
    :return:  list of WhiteSource Products (dictionaries)
    """
    def convert_gh_org_name_to_ws_prod_name(name) -> str:
        """
        Convert Given GH Organization name to WhiteSource Product name
        :param name:
        :return:
        """
        fix_name = name
        logging.debug(f"Fixed name from {name} to {fix_name}")

        return fix_name

    def convert_gh_org_to_ws_prod(gh_org_n: str) -> dict:
        """
        Convert a single GH Organization to WhiteSource Product
        :param gh_org_n:
        :return: WS Product (dictionary)
        """
        ws_prod_name = convert_gh_org_name_to_ws_prod_name(gh_org_n)
        prod = all_prods_dict.get(ws_prod_name)                      # Filtering out non-existing GH Organizations
        if prod:
            logging.debug(f"Found WS Product: {prod['name']} Token: {prod['token']} Org Token: {prod['org_token']}")
        else:
            logging.warning(f"GitHub organization: {gh_org_n} (WS Product name: {ws_prod_name}) was not found")

        return prod
    global config
    logging.debug("Converting GitHub Organization names to WS Product names")
    all_prods_in_global_org = config['ws_conn_global'].get_scopes(scope_type=ws_constants.PRODUCT)
    all_prods_dict = ws_utilities.convert_dict_list_to_dict(all_prods_in_global_org, "name")
    ws_prods = []
    for gh_org_name in gh_org_names:
        curr_prod = convert_gh_org_to_ws_prod(gh_org_name)
        ws_prods.append(curr_prod)

    return ws_prods


class CreateUserRequest(BaseModel):
    user: str
    email: str
    role: str
    gh_org_names: list


@api.put("/create_user_in_ws")
async def api_create_user_in_ws_products(create_user_req: CreateUserRequest,
                                         request: Request):
    return create_user_in_ws_products(username=create_user_req.user,
                                      email=create_user_req.email,
                                      role=create_user_req.role,
                                      gh_org_names=create_user_req.gh_org_names)


def create_user_in_ws_products(username: str, email: str, role: str, gh_org_names: list) -> dict:
    def is_valid_user():
        return True

    if not is_valid_user():
        logging.error(f"Invalid Username: {username}")
    elif role not in ws_constants.RoleTypes.PROD_ROLES_TYPES:
        logging.error(f"Invalid Role: {role}")
    elif not is_valid_email():
        logging.error(f"Invalid Email: {email}")
    else:
        ws_prods = convert_gh_orgs_to_ws_prods(gh_org_names)

        org_tokens = set()
        for ws_prod in ws_prods:
            logging.debug(f"Handling Product: {ws_prod['name']} Token: {ws_prod['token']} Organization token: {ws_prod['org_token']}")
            tmp_conn = WS(user_key=config['ws_conn_global'].user_key,
                          token=ws_prod['org_token'],
                          url=config['ws_conn_global'].url)
            # Actions that are only necessary once on an organization
            if ws_prod['org_token'] not in org_tokens:
                logging.debug(f"Creating user: {username} and Group: {role} on Organization: {ws_prod['org_token']}")
                org_tokens.add(ws_prod['org_token'])
                cu = tmp_conn.create_user(username, email, config['InviterEmail'])
                cg = tmp_conn.create_group(role)
                autg = tmp_conn.assign_user_to_group(email, role)

            atg = tmp_conn.assign_to_scope(role_type=role, group=role, token=ws_prod['token'])

        return create_response({})


class DeleteUserRequest(BaseModel):
    email: str
    gh_org_names: list


@api.put("/delete_user_from_ws")
async def api_delete_user_from_ws(delete_user_req: DeleteUserRequest,
                                  request: Request):
    return delete_user_from_ws(email=delete_user_req.email,
                               gh_org_names=delete_user_req.gh_org_names)


def delete_user_from_ws(email, gh_org_names):
    if not is_valid_email():
        logging.error(f"Invalid Email: {email}")
    else:
        ws_prods = convert_gh_orgs_to_ws_prods(gh_org_names)
        org_tokens = set()
        for prod in ws_prods:
            org_tokens.add(prod['org_token'])

        for token in org_tokens:
            config['ws_conn_global'].delete_user(email=email, org_token=token)

        return create_response({})


def is_valid_email():
    return True


def create_response(payload, status=200):
    return json.dumps(payload), status, {'content-type': 'application/json'}


def check_config():
    for k, v in config.items():
        if v is None:
            logging.error(f"Missing environment variable: {k.upper()}")
            return False

    return True


if __name__ == '__main__':
    if check_config():
        uvicorn.run(app="app:api", host="0.0.0.0", port=8000, reload=False, debug=False)
    else:
        logging.error("Error starting Uvicorn")
    # init()
    # ret = create_user_in_ws_products(username="TEST",
    #                                  email="test1@test.com",
    #                                  role=ws_constants.RoleTypes.P_ALERT_RECEIVERS,
    #                                  gh_org_names=["nexus", 'WebGoat', 'fuzz1'])
    #
    # ret = delete_user_from_ws(email="test1@test.com",
    #                           gh_org_names=["nexus", 'WebGoat', 'fuzz1'])
