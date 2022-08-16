# this script downloads the JSON files containing the inline comments of every revision of the project specified in the settings
# the inline comments JSON files are saved in the 'inline_comments_details' dir

from urllib.request import *
from commons import get_repo_name, load_config, rg_id, compare_review_json, filter_json
from logger import init_logger
import os
import glob
import json
import logging


repo_name = get_repo_name()
config = load_config(repo_name)
init_logger("%s-inline-comments.log" % repo_name)

COMMUNITY = config['community']
PROJECT_REVIEW_JSON = config['project_review_json']
INLINE_COMMENT_URL=config['inline_comment_url']

# create the inline_comments_details directory if it does not exist
if not os.path.isdir("inline_comments_details"):
    os.mkdir("inline_comments_details")

# create an inline comments details directory for the project if it does not exist
if not os.path.isdir("inline_comments_details/" + COMMUNITY):
    os.mkdir("inline_comments_details/" + COMMUNITY)

# get the reviews' details JSON files for the community sorted in ascending order
review_jsons = sorted(glob.glob("reviews_details/" + COMMUNITY + "/*.json"), key=compare_review_json)

# we iterate over all review's JSON files, filtering the ones regarding the project of interest
for review_json in review_jsons:
    review_number = rg_id.findall(review_json)[0]

    review_json = json.load(open(review_json))

    # iterate over all revisions, sorted by the revision number
    for key, value in sorted(review_json["revisions"].items(), key=lambda revision_item: int(revision_item[1]["_number"])):
        revision_number = str(value["_number"])
        inline_comment_file_name = "inline_comments_details/%s/%s_rev_%s.json" % (COMMUNITY, review_number, revision_number)

        # if inline comment file already exists, skip to next
        if os.path.isfile(inline_comment_file_name):
            continue

        inline_comment_url = INLINE_COMMENT_URL % (review_number, revision_number)
        try:
            logging.info("%s %s", inline_comment_file_name, inline_comment_url)
            resp = urlopen(inline_comment_url)
        except Exception as e:
            logging.error(e, exc_info=True)
            continue

        content = filter_json(resp)
        with open(inline_comment_file_name, "w") as f:
            f.write(content)
