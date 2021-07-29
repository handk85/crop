# this script downloads the JSON files containing the details of every review in a certain community
# the reviews JSON files are saved in the 'reviews_details' dir

import logging
import os
from logger import init_logger
from commons import get_repo_name, load_config, filter_json
from urllib.request import *

repo_name = get_repo_name()
init_logger("%s-reviews-detail.log" % repo_name)
config = load_config(repo_name)

COMMUNITY = config['community']
REVIEW_URL = config['review_json_url']
START_INDEX = int(config['start_index'])
END_INDEX = int(config['end_index']) + 1

# create the reviews_details directory if it does not exist
if not os.path.isdir("reviews_details"):
    os.mkdir("reviews_details")

# create the directory to store the reviews details for the community if it does not exist
if not os.path.isdir("reviews_details/" + COMMUNITY):
    os.mkdir("reviews_details/" + COMMUNITY)

for i in range(START_INDEX, END_INDEX):
    file_name = "reviews_details/" + COMMUNITY + "/%s.json" % i

    # if JSON file is already downloaded, skip to next review
    if os.path.isfile(file_name):
        continue

    review_url = REVIEW_URL % i

    # if any error in downloading the JSON, skip to next review
    try:
        logging.info("%s %s", file_name, review_url)
        resp = urlopen(review_url)
    except Exception as e:
        logging.error(e, exc_info=True)
        continue

    content = filter_json(resp)
    with open(file_name, "w") as f:
        f.write(content)
