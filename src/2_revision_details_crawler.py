# this script downloads the JSON files containing the details of every revision of the project specified in the settings
# the revision JSON files are saved in the 'revisions_details' dir

from urllib.request import *
from commons import get_repo_name, load_config, rg_id, compare_review_json, filter_json
from logger import init_logger
import os
import glob
import json
import logging

repo_name = get_repo_name()
config = load_config(repo_name)
init_logger("%s-revision_details.log" % repo_name)

COMMUNITY = config['community']
PROJECT_REVIEW_JSON = config['project_review_json']
REVISION_JSON_URL=config['revision_json_url']

# create the revisions_details directory if it does not exist
if not os.path.isdir("revisions_details"):
    os.mkdir("revisions_details")

# create a revisions details directory for the project if it does not exist
if not os.path.isdir("revisions_details/" + COMMUNITY):
    os.mkdir("revisions_details/" + COMMUNITY)

# get the reviews' details JSON files for the community sorted in ascending order
review_jsons = sorted(glob.glob("reviews_details/%s/*.json" % COMMUNITY), key=compare_review_json)

# we iterate over all JSON files, filtering the ones regarding the project of interest and
# downloading the necessary revisions details
for review_json in review_jsons:
    review_number = rg_id.findall(review_json)[0]

    json_file = json.load(open(review_json))

    for key, value in json_file["revisions"].items():
        revision_number = str(value["_number"])
        revision_file_name = "revisions_details/%s/%s_rev_%s.json" % (COMMUNITY, review_number, revision_number)

        # if revision file already exists, skip to next
        if os.path.isfile(revision_file_name):
            continue

        revision_url = REVISION_JSON_URL % (review_number, key)

        try:
            logging.info("%s %s", revision_file_name, revision_url)
            resp = urlopen(revision_url)
        except Exception as e:
            logging.error(e, exc_info=True)
            continue

        content = filter_json(resp)
        with open(revision_file_name, "w") as f:
            f.write(content)
