import requests
import os
import shutil
import zipfile
import glob

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

session = requests.Session()
retries = Retry(total=10, backoff_factor=0.3)
session.mount('https://github.com', HTTPAdapter(max_retries=retries))

MIN_GITHUB_STARS = 10

def get_github_repo_names():
    with open('github-repos.csv', 'r') as f:
        lines = f.readlines()
        repos = map(lambda x: x.rstrip().split(','), lines)
        repos = filter(lambda r: int(r[2]) >= MIN_GITHUB_STARS, repos)
        return repos

def make_url(repo_name, branch="master"):
    return "https://github.com/%s/%s/archive/%s.zip" % (repo_name[0], repo_name[1], branch)

def make_dir_path(work_dir, repo_name):
    return os.path.join(work_dir, repo_name[0], repo_name[1])

def remove_empty_dirs(path):
    while True:
        to_delete = []
        for root, dirs, files in os.walk(path):
            if files: continue
            if dirs: continue
            to_delete.append(root)

        if to_delete:
            for p in to_delete:
                shutil.rmtree(p)
        else:
            break

def download_repo(repo_name, repo_dir):
    r = session.get(make_url(repo_name), stream=True)
    zip_path = os.path.join(repo_dir, "repo.zip")
    if r.status_code == 200:
        with open(zip_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    elif r.status_code == 404:
        print("Repo moved? Skipping!")
        return
    else:
        raise Exception("Non-200 status! Status: " + str(r.status_code))

    zip_ref = zipfile.ZipFile(zip_path, 'r')
    zip_ref.extractall(repo_dir)
    zip_ref.close()
    os.remove(zip_path)

    # Move everything from the sub dir back up to repo level
    dir_in_zip = os.listdir(repo_dir)[0]
    for f in os.listdir(os.path.join(repo_dir, dir_in_zip)):
        shutil.move(os.path.join(repo_dir, dir_in_zip, f), os.path.join(repo_dir, f))

    shutil.rmtree(os.path.join(repo_dir, dir_in_zip))

    def should_keep_file(filename):
        if 'readme' in filename.lower(): return True
        if 'license' in filename.lower(): return True
        if 'workspace' == filename.lower(): return True
        if 'build' == filename.lower(): return True
        if 'build.bazel' == filename.lower(): return True
        if '.bzl' in filename.lower(): return True
        return False

    # Strip non-Bazel related files
    files_to_remove = []
    for root, dirs, files in os.walk(repo_dir):
        for f in files:
            if not should_keep_file(f):
                files_to_remove.append(os.path.join(root, f))

    for f in files_to_remove:
        os.remove(f)

    remove_empty_dirs(repo_dir)


def main():
    work_dir = "work"

    repo_names = get_github_repo_names()
    for repo_name in repo_names:
        repo_dir = make_dir_path(work_dir, repo_name)
        if os.path.exists(repo_dir):
            print("Repo already downloaded!")
            continue

        os.makedirs(repo_dir)
        print("Downloading %s/%s..." % (repo_name[0], repo_name[1]))
        download_repo(repo_name, repo_dir)

main()
