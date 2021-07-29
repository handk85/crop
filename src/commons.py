import re
import sys
import socket
import configparser

socket.setdefaulttimeout(50)
# regex object to extract the review number from the review JSON file
rg_id = re.compile("/(\d+)\.json")


def get_repo_name():
    if len(sys.argv) < 2:
        print("Please specify repo name")
        sys.exit(0)
    return sys.argv[1].upper()


def load_config(repo_name:str):
    config_parser = configparser.ConfigParser()
    config_parser.read("settings.ini")
    return config_parser[repo_name]


# function to compare the review's JSON files when sorting
def compare_review_json(review_json_file_name):
    splitted_review_json_file_name = review_json_file_name.split("/")

    return int(splitted_review_json_file_name[len(splitted_review_json_file_name) - 1].split(".")[0])


def filter_json(resp: any):
    content = resp.read().decode("utf-8", errors="ignore")

    # JSONs returned by the Gerrit API usually have a non-standard starting line that needs to be filtered
    if content.startswith(")]}'"):
        content = "\n".join(content.split("\n")[1:])
    return content
