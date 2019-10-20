import argparse
import collections
import configparser
import hashlib
import logging
import os
import re
import sys
import zlib

logger = logging.Logger(__name__)

argparser = argparse.ArgumentParser(description='The humble version control')

argsubparsers = argparser.add_subparsers(title='Commands', dest='command')

argsubparsers.required = True


def repo_path(repository, *path):
    """Compute path under repo's gitdir"""
    return os.path.join(repository.gitdir, *path)


def repo_file(repo, *path, mkdir=False):
    """Compute path under repo's gitdir but creates directory if computed directory absent.
    :param repo:
    :param path:
    :param mkdir:
    :return:
    :example:

    >> repo_file(r, \'refs\', \'remotes\', \'origin\', \'HEAD\')
    .git/refs/remotes/origin
    """
    if repo_dir(repo, *path, mkdir=mkdir):
        return repo_path(repo, path)


def repo_dir(repo, *path, mkdir=False):
    """Compute gitdir path and create directory if not present
    :param repo:
    :param path:
    :return:
    """
    path = repo_path(repo, *path)

    if os.path.exists(path):
        if os.path.isdir(path):
            return path

        else:
            raise Exception(f'Not a directory ${path}')

    if mkdir:
        os.makedirs(path)
    else:
        return None


def repo_create(path):
    """Create a new repository at path"""
    repo = GitRepository(path, force=True)

    # ensure that path is empty or doesn't exist
    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception(f'${path} is not a directory')
        if os.listdir(repo.worktree):
            raise Exception(f'${path} is not empty')
    else:
        os.makedirs(repo.worktree)

    assert(repo_dir(repo, 'branches', mkdir=True))
    assert(repo_dir(repo, 'objects', mkdir=True))
    assert(repo_dir(repo, 'refs', 'tags', mkdir=True))
    assert(repo_dir(repo, 'refs', 'tags', mkdir=True))

    # .git/ description
    with open(repo_file(repo, 'description'), 'w') as f:
        f.write('Unnamed repository; edit this file \'description\' to name the repository.\n')

    with open(repo_file(repo, 'head'), 'w') as f:
        f.write('ref: refs/heads/master\n')

    with open(repo_file(repo, 'config'), 'w') as f:
        config = repo_default_config()
        config.write(f)

    return repo


def repo_default_config():
    config = configparser.ConfigParser()
    config.add_section('core')
    config.set('core', 'repositoryformatversion', '0')
    config.set('core', 'filemode', 'false')
    config.set('core', 'bare', 'false')

    return config


argsp = argsubparsers.add_parser('init', help='Initialize a new, empty repository')
argsp.add_argument('path',
                   metavar='directory',
                   nargs='?',
                   default='.',
                   help='Where to create the repository.'
                   )


def cmd_init(args):
    repo_create(args.path)


class GitRepository:
    """Represents a Git repository"""

    config = None
    worktree = None
    gitdir = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path.join(path, '.git')

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f'Not a Git repository {path}')

        # Read config
        self.config = configparser.ConfigParser()
        cf = repo_file(self, 'config')

        if cf and os.path.exists(cf):
            self.config.read([cf])
        elif not force:
            raise Exception('Configuration file missing')

        if not force:
            version = int(self.config.get('core', 'repositoryformatversion'))
            if version != 0:
                raise Exception(f'Unsupported repositoryformatversion {version}')


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    command = args.command

    command_map = {
        'add': cmd_add,
        'cat-file': cmd_cat_file,
        'checkout': cmd_checkout,
        'commit': cmd_commit,
        'hash-object': cmd_hash_object,
        'init': cmd_init,
        'log': cmd_log,
        'ls-tree': cmd_ls_tree,
        'merge': cmd_merge,
        'rebase': cmd_rebase,
        'rev-parse': cmd_rev_parse,
        'rm': cmd_rm,
        'show-ref': cmd_show_ref,
        'tag': cmd_tag
    }

    cmd_command = command_map.get(command)
    if callable(cmd_command):
        return cmd_command(args)
    else:
        logging.error(msg=f'Command {args} not found')
