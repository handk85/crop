from urllib.request import *
from commons import get_repo_name, load_config, rg_id, compare_review_json, filter_json
from logger import init_logger
import os
import glob
import json
import logging
import base64


repo_name = get_repo_name()
config = load_config(repo_name)
init_logger("%s-inline-comments.log" % repo_name)

COMMUNITY = config['community']
PROJECT_REVIEW_JSON = config['project_review_json']
DIFF_URL=config['patch_url']


# create the inline_comments_details directory if it does not exist
if not os.path.isdir("diffs"):
    os.mkdir("diffs")

# create an inline comments details directory for the project if it does not exist
if not os.path.isdir("diffs/" + COMMUNITY):
    os.mkdir("diffs/" + COMMUNITY)

# get the reviews' details JSON files for the community sorted in ascending order
review_jsons = sorted(glob.glob("reviews_details/" + COMMUNITY + "/*.json"), key=compare_review_json)

for review_json in review_jsons:
    review_number = rg_id.findall(review_json)[0]

    review_json = json.load(open(review_json))

    for key, value in sorted(review_json["revisions"].items(), key=lambda revision_item: int(revision_item[1]["_number"])):
        revision_number = str(value["_number"])
        diff_file_name = "diffs/%s/%s_diff_%s.diff" % (COMMUNITY, review_number, revision_number)

        # if inline comment file already exists, skip to next
        if os.path.isfile(diff_file_name):
            continue

        diff_url = DIFF_URL % (review_number, revision_number)
        try:
            logging.info("%s %s", diff_file_name, diff_url)
            resp = urlopen(diff_url)
            raw_content = resp.read()
            content = base64.b64decode(raw_content)
            content = content.decode('utf-8', errors='ignore')
        except Exception as e:
            logging.error(e, exc_info=True)
            continue

        with open(diff_file_name, "w") as f:
            f.write(content)
