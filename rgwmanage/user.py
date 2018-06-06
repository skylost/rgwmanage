#!/usr/bin/env python

import os
import re
import sys
import json
import copy
import subprocess
import logging
from cliff.command import Command
from cliff.show import ShowOne
from cliff.lister import Lister

class ListUsers(Lister):

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ListUsers, self).get_parser(prog_name)
        parser.add_argument('--long',
                            action='store_true',
                            default=False,
                            help="List additional fields in output")
        return parser

    def take_action(self, parsed_args):
        cmd_rgw_user_list = 'radosgw-admin metadata list user'
        rgw_user_list = subprocess.check_output(cmd_rgw_user_list, shell=True,
                                             stderr=subprocess.STDOUT)
        l = ()
        if parsed_args.long:
            columns = ('Name', 'ID', 'Default placement',
                       'Max buckets','Bucket quota', 'User quota')
            for k in json.loads(rgw_user_list):
                cmd_user_get = "radosgw-admin metadata get user:'%s'" % k
                user_get = subprocess.check_output(cmd_user_get, shell=True,
                                                stderr=subprocess.STDOUT)
                u = json.loads(user_get)
                line = (u['data']['display_name'], k,
                        u['data']['default_placement'],
                        u['data']['max_buckets'],
                        u['data']['bucket_quota']['enabled'],
                        u['data']['user_quota']['enabled'],)
                l = l + (line, )
        else:
            columns = ('Name', 'ID', 'Default placement')
            for k in json.loads(rgw_user_list):
                cmd_user_get = "radosgw-admin metadata get user:'%s'" % k
                user_get = subprocess.check_output(cmd_user_get, shell=True,
                                                stderr=subprocess.STDOUT)
                u = json.loads(user_get)
                line = (u['data']['display_name'], k.split('$',1)[0],
                        u['data']['default_placement'],)
                l = l + (line, )

        return columns, l

class ShowUser(ShowOne):

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ShowUser, self).get_parser(prog_name)
        parser.add_argument('id', help="User id")
        return parser

    def take_action(self, parsed_args):
        cmd_rgw_user_list = 'radosgw-admin metadata list user'
        rgw_user_list = subprocess.check_output(cmd_rgw_user_list, shell=True,
                                             stderr=subprocess.STDOUT)
        cmd_user = "radosgw-admin metadata get user:'%s'" % parsed_args.id
        user = subprocess.check_output(cmd_user, shell=True,
                                            stderr=subprocess.STDOUT)
        json_user= json.loads(user)

        columns = ('ID',
                   'Display name',
                   'Creation date',
                   'Default placement',
                   'Placement tags',
                   'Max buckets',
                   'Bucket quota enabled',
                   'Bucket quota max size kb',
                   'Bucket quota max objects',
                   'User quota enabled',
                   'User quota max size kb',
                   'User quota max objects',
                   )
        data = (parsed_args.id,
                json_user['data']['display_name'],
                json_user['mtime'],
                json_user['data']['default_placement'],
                json_user['data']['placement_tags'],
                json_user['data']['max_buckets'],
                json_user['data']['bucket_quota']['enabled'],
                json_user['data']['bucket_quota']['max_size_kb'],
                json_user['data']['bucket_quota']['max_objects'],
                json_user['data']['user_quota']['enabled'],
                json_user['data']['user_quota']['max_size_kb'],
                json_user['data']['user_quota']['max_objects'],
                )
        return (columns, data)

class UpdateUser(ShowOne):

   def get_parser(self, prog_name):
        parser = super(UpdateUser, self).get_parser(prog_name)
        parser.add_argument('id', help="User id")
        parser.add_argument('--default-placement',
                            help="Default placement")
        parser.add_argument('--max-buckets',
                            help="Max buckets",
                            type=int)
        bucket_quota_group = parser.add_mutually_exclusive_group()
        bucket_quota_group.add_argument('--bucket-quota-enabled',
                            help="Bucket quota enabled",
                            action='store_true')
        bucket_quota_group.add_argument('--no-bucket-quota-enabled',
                             help="Bucket quota disabled",
                             action='store_true')
        parser.add_argument('--bucket-quota-max-size-kb',
                            help="Bucket quota max size kb",
                            type=int)
        parser.add_argument('--bucket-quota-max-objects',
                            help="Bucket quota max objects",
                            type=int)
        user_quota_group = parser.add_mutually_exclusive_group()
        user_quota_group.add_argument('--user-quota-enabled',
                            help="User quota enabled",
                            action='store_true')
        user_quota_group.add_argument('--no-user-quota-enabled',
                             help="User quota disabled",
                             action='store_true')
        parser.add_argument('--user-quota-max-size-kb',
                            help="User quota max size kb",
                            type=int)
        parser.add_argument('--user-quota-max-objects',
                            help="User quota max objects",
                            type=int)
        return parser

   def take_action(self, parsed_args):
        cmd_user = "radosgw-admin metadata get user:'%s'" % parsed_args.id
        user = subprocess.check_output(cmd_user, shell=True,
                                        stderr=subprocess.STDOUT)
        json_user = json.loads(user)

        json_user_new = copy.copy(json_user)

        if parsed_args.default_placement:
            json_user_new['data']['default_placement'] = parsed_args.default_placement
        if parsed_args.max_buckets:
            json_user_new['data']['max_buckets'] = parsed_args.max_buckets
        if parsed_args.bucket_quota_max_size_kb:
            json_user_new['data']['bucket_quota']['max_size_kb'] = parsed_args.bucket_quota_max_size_kb
        if parsed_args.bucket_quota_max_objects:
            json_user_new['data']['bucket_quota']['max_objects'] = parsed_args.bucket_quota_max_objects
        if parsed_args.user_quota_max_size_kb:
            json_user_new['data']['user_quota']['max_size_kb'] = parsed_args.user_quota_max_size_kb
        if parsed_args.user_quota_max_objects:
            json_user_new['data']['user_quota']['max_objects'] = parsed_args.user_quota_max_objects
        if parsed_args.bucket_quota_enabled:
            json_user_new['data']['bucket_quota']['enabled'] = parsed_args.bucket_quota_enabled
        if parsed_args.no_bucket_quota_enabled:
            json_user_new['data']['bucket_quota']['enabled'] = False
        if parsed_args.user_quota_enabled:
            json_user_new['data']['user_quota']['enabled'] = parsed_args.user_quota_enabled
        if parsed_args.no_user_quota_enabled:
            json_user_new['data']['user_quota']['enabled'] = False

        dump_user_new = json.dumps(json_user_new)
        put_user = ["radosgw-admin", "metadata", "put", "user:'%s'" % parsed_args.id ]
        process = subprocess.Popen(put_user, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        process.stdin.write(dump_user_new)
        process.stdin.close()
        process.wait()

        columns = ('ID',
                   'Default placement',
                   'Placement tags',
                   'Max buckets',
                   'Bucket quota enabled',
                   'Bucket quota max size kb',
                   'Bucket quota max objects',
                   'User quota enabled',
                   'User quota max size kb',
                   'User quota max objects',
                   )
        data = (parsed_args.id,
                json_user_new['data']['default_placement'],
                json_user_new['data']['placement_tags'],
                json_user_new['data']['max_buckets'],
                json_user_new['data']['bucket_quota']['enabled'],
                json_user_new['data']['bucket_quota']['max_size_kb'],
                json_user_new['data']['bucket_quota']['max_objects'],
                json_user_new['data']['user_quota']['enabled'],
                json_user_new['data']['user_quota']['max_size_kb'],
                json_user_new['data']['user_quota']['max_objects'],
                )
        return (columns, data)

class UpdateUserAll(Lister):

   def get_parser(self, prog_name):
        parser = super(UpdateUserAll, self).get_parser(prog_name)
        parser.add_argument('--default-placement',
                            help="Default placement")
        parser.add_argument('--default-user-quota',
                            help="Default user quota enabled",
                            action='store_true')
        return parser

   def take_action(self, parsed_args):
        cmd_rgw_user_list = 'radosgw-admin metadata list user'
        rgw_user_list = subprocess.check_output(cmd_rgw_user_list, shell=True,
                                                stderr=subprocess.STDOUT)
        l = ()
        for k in json.loads(rgw_user_list):
            cmd_user = "radosgw-admin metadata get user:'%s'" % k
            user = subprocess.check_output(cmd_user, shell=True,
                                            stderr=subprocess.STDOUT)
            json_user = json.loads(user)
            json_user_new = copy.copy(json_user)
            update = False

            if parsed_args.default_placement:
                if not json_user['data']['default_placement']:
                    json_user_new['data']['default_placement'] = parsed_args.default_placement
                    update = True

            if parsed_args.default_user_quota:
                if not json_user['data']['user_quota']['enabled']:
                    json_user_new['data']['user_quota']['enabled'] = parsed_args.default_user_quota
                    update = True
                if json_user['data']['user_quota']['max_size_kb'] == -1:
                    json_user_new['data']['user_quota']['max_size_kb'] = 10000000
                    update = True

            if update:
                dump_user_new = json.dumps(json_user_new)
                put_user = ["radosgw-admin", "metadata", "put", "user:'%s'" % k ]
                process = subprocess.Popen(put_user, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                process.stdin.write(dump_user_new)
                process.stdin.close()
                process.wait()

            line = (json_user_new['data']['display_name'], k.split('$',1)[0],
                    json_user_new['data']['default_placement'],
                    json_user_new['data']['max_buckets'],
                    json_user_new['data']['bucket_quota']['enabled'],
                    json_user_new['data']['user_quota']['enabled'],
                    json_user_new['data']['user_quota']['max_size_kb'],
                    json_user_new['data']['user_quota']['max_objects'],
                    update,)

            columns = ('Name', 'ID', 'Default placement',
                       'Max buckets','Bucket quota', 'User quota',
                       'User quota max size kb', 'User quota max objects',
                       'Update',)
            l = l + (line, )

        return (columns, l)
