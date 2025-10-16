import time
import json

def getTimeInMs(startTime, endTime):
    returnTime = (endTime - startTime) * 1000
    return f"{returnTime:.2f}"


def parse_dist_params(degree_mode="low_degree", filetype_mode="default", file_ext_mode="default", permissions_mode="default", size_mode="default"):
    
    # Load JSON from file
    with open("dists/params.json", 'r') as f:
        params = json.load(f)

    # Degree
    degree_distr = {int(k): v for k, v in params["degree"][degree_mode].items()}
    # File type
    fileType_distr = {k: v for k, v in params["type"][filetype_mode].items()}
    # Extensions
    fileExt_distr = {k: v for k, v in params["filetypes"][file_ext_mode].items()}
    # Permissions
    permissions_distr = {int(k, 8): v for k, v in params["permissions"][permissions_mode].items()}
    # Sizes
    size_distr = {k: v for k, v in params["size"][size_mode].items()}

    return degree_distr, fileType_distr, fileExt_distr, permissions_distr, size_distr


def parse_edit_params(edit_mode="default"):
    
    # Load JSON from file
    with open("dists/params.json", 'r') as f:
        params = json.load(f)

    # Degree
    modify_dist = {k: v for k, v in params["modify"][edit_mode].items()}
    
    return modify_dist
