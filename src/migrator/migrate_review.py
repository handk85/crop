from database import init_db
import sys
import json
import glob
import logging
import configparser

from database import init_db, get_keys, get_ids_from_database, insert_data

sys.path.append('../')
from logger import init_logger
from commons import get_repo_name

init_logger("migrate_review.log")
repo_name = get_repo_name()

config = configparser.ConfigParser()
config.read("database.ini")

COMMUNITY = config[repo_name]['community']
REVIEW_USER_KEYS = ["submitter", "owner"]
MESSAGE_USER_KEYS = ["author", "real_author"]

db_config = config["DATABASE"]
db_config["database"] = config[repo_name]["database"]
conn = init_db(db_config)
cur = conn.cursor()
keys = get_keys(cur)


def extract_user(node: dict):
    user = {k: v for k, v in node.items() if k in keys["user"]}
    # Annonymise username
    user["username"] = str(hash(user["username"]))
    return user

def extract_labels(l: list, label_type: str, users: list):
    labels = []
    for item in l:
        users.append(extract_user(item))
        l_data = {k: v for k, v in item.items() if k in keys["label"]}
        l_data["review_id"] = j["_number"]
        l_data["label_type"] = label_type 
        l_data["user_id"] = item["_account_id"]
        labels.append(l_data)
    return labels


existing_review_ids = get_ids_from_database(cur, "review", "_number")
existing_user_ids = get_ids_from_database(cur, "user", "_account_id")
# Review migration
for f_name in glob.glob("../reviews_details/%s/*.json" % COMMUNITY):
    logging.info(f_name)
    with open(f_name) as f:
        content = f.read()
    
    j = json.loads(content)
    if j["_number"] in existing_review_ids:
        logging.info("Review %s already exists" % j["_number"])
        continue

    # Submitter can be missing e.g., Review 195153
    users = [extract_user(j[k]) for k in REVIEW_USER_KEYS if k in j]

    review_data = {k: v for k,v in j.items() if k in keys["review"]}
    [review_data.update({("%s_id" % k): v["_account_id"] for k, v in j.items() if k in REVIEW_USER_KEYS})]

    messages = []
    for m in j["messages"]:
        m_data = {k: v for k, v in m.items() if k in keys["messages"]}
        m_data["review_id"] = j["_number"]
        users += [extract_user(m[k]) for k in MESSAGE_USER_KEYS]
        [m_data.update({("%s_id" % k): v["_account_id"] for k, v in m.items() if k in MESSAGE_USER_KEYS})]
        messages.append(m_data)
    
    revisions = []
    for rev_id in j["revisions"].keys():
        rev = j["revisions"][rev_id]
        r_data = {k: v for k, v in rev.items() if k in keys["revision"]}
        r_data["id"] = rev_id
        r_data["review_id"] = j["_number"]
        users.append(extract_user(rev["uploader"])) 
        r_data["uploader_id"] = rev["uploader"]["_account_id"]
        revisions.append(r_data)
    
    labels = []
    for label_type, item in j["labels"].items():
        labels += extract_labels(item["all"], label_type, users)
    
    for user in users:
        if user["_account_id"] not in existing_user_ids:
            insert_data(cur, "user", user) 
            existing_user_ids.append(user["_account_id"])

    insert_data(cur, "review", review_data)
    [insert_data(cur, "messages", m) for m in messages]
    [insert_data(cur, "revision", r) for r in revisions]
    [insert_data(cur, "label", l) for l in labels]

    conn.commit()

