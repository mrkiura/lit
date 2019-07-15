import argparse
import collections
import configparser
import hashlib
import os
import re
import sys
import zlib

argparser = argparse.ArgumentParser(description="The humble version control")

argsubparsers = argparser.add_subparsers(title="Commands", dest="command")

argsubparsers.required = True


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    command = args.command
    command_map = {
        "add": cmd_add,
        "cat-file": cmd_cat_file,
        "checkout": cmd_checkout(args),
        "commit": cmd_commit(args),
        "hash-object": cmd_hash_object(args),
        "init": cmd_init(args),
        "log": cmd_log(args),
        "ls-tree": cmd_ls_tree(args),
        "merge": cmd_merge(args),
        "rebase": cmd_rebase(args),
        "rev-parse": cmd_rev_parse(args),
        "rm": cmd_rm(args),
        "show-ref": cmd_show_ref(args),
        "tag": cmd_tag(args)

    }
    return command_map.get(command)(args)
