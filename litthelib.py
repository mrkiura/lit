import argparse
import collections
import configparser
import hashlib
import os
import re
import sys
import zlib
import logging

logger = logging.Logger(__name__)

argparser = argparse.ArgumentParser(description="The humble version control")

argsubparsers = argparser.add_subparsers(title="Commands", dest="command")

argsubparsers.required = True


def repo_file():
    return


def repo_path(repository, *path):
    """"
    Compute path under repo's gitdir
    """
    return os.path.join(repository.gitdir, *path)


def repo_fil(repo, *path):
    pass



class GitRepository:
    """Represents a Git repository"""

    config = None
    worktree = None
    gitdir = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f"Not a Git repository {path}")

        # Read config
        self.config = configparser.ConfigParser()
        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.config.read([cf])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            version = int(self.config.get("core", "repositoryformatversion"))
            if version != 0:
                raise Exception(f"Unsupported repositoryformatversion {version}")

def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    command = args.command

    command_map = {
        "add": cmd_add,
        "cat-file": cmd_cat_file,
        "checkout": cmd_checkout,
        "commit": cmd_commit,
        "hash-object": cmd_hash_object,
        "init": cmd_init,
        "log": cmd_log,
        "ls-tree": cmd_ls_tree,
        "merge": cmd_merge,
        "rebase": cmd_rebase,
        "rev-parse": cmd_rev_parse,
        "rm": cmd_rm,
        "show-ref": cmd_show_ref,
        "tag": cmd_tag
    }
    
    cmd_command = command_map.get(command)
    if callable(cmd_command):
        return cmd_command(args)
    else:
        logging.error(msg="Command {args} not found".format(args))
