#!/usr/bin/env python

import os
import re
import sys
import logging
import rgwmanage.user
from cliff.app import App
from cliff.commandmanager import CommandManager

class radosgwShell(App):

    log = logging.getLogger(__name__)

    def __init__(self):
        command = CommandManager('rgwmanage.shell')
        super(radosgwShell, self).__init__(
            description='Ceph Rados gateway manage',
            version='0.1',
            command_manager=command,
        )
        commands = {
            'user-list': rgwmanage.user.ListUsers,
            'user-show': rgwmanage.user.ShowUser,
            'user-update': rgwmanage.user.UpdateUser,
            'user-update-all': rgwmanage.user.UpdateUserAll,
        }
        for k, v in commands.iteritems():
            command.add_command(k, v)

    def initialize_app(self, argv):
        self.log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)

def main(argv=sys.argv[1:]):
    return radosgwShell().run(argv)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
