from database import init_db
import re
import sys
import json
import glob
import logging
import configparser

from database import init_db, get_keys, get_ids_from_database, insert_data

sys.path.append('../')
from logger import init_logger
from commons import get_repo_name

init_logger("migrate_inline_comments.log")
repo_name = get_repo_name()

config = configparser.ConfigParser()
config.read("database.ini")

COMMUNITY = config[repo_name]['community']
REVIEW_USER_KEYS = ["submitter", "owner"]
MESSAGE_USER_KEYS = ["author", "real_author"]

rg_rev_info = re.compile("([0-9]*)_rev_([0-9]*)\.json")

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


existing_comment_ids = get_ids_from_database(cur, "inline_comments", "id")
existing_user_ids = get_ids_from_database(cur, "user", "_account_id")
# Review migration
for f_name in glob.glob("../inline_comments_details/%s/*.json" % COMMUNITY):
    logging.info(f_name)
    rev_info = rg_rev_info.findall(f_name)[0]
    with open(f_name) as f:
        content = f.read()
    
    j = json.loads(content)

    authors = []
    comments = []
    for item in j.keys():
        for comment in j[item]:
            if comment["id"] in existing_comment_ids:
                logging.info("Inline_comment %s already exists" % j["_number"])
                continue
            comment_data = {k: v for k, v in comment.items() if k in keys["inline_comments"]}
            authors.append(extract_user(comment["author"]))
            comment_data["file_name"] = item
            comment_data["author_id"] = comment["author"]["_account_id"]
            comment_data["review_id"] = rev_info[0]
            comment_data["_revision_number"] = rev_info[1]
            if "range" in comment:
                comment_data.update(comment["range"])
            comments.append(comment_data)

    for user in authors:
        if user["_account_id"] not in existing_user_ids:
            insert_data(cur, "user", user) 
            existing_user_ids.append(user["_account_id"])
    
    [insert_data(cur, "inline_comments", c) for c in comments]

    conn.commit()

