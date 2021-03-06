# -*- coding: utf-8 -*-
'''
Apache state

Allows for inputting a yaml dictionary into a file for apache configuration
files.

The variable ``this`` is special and signifies what should be included with
the above word between angle brackets (<>).

.. code-block:: yaml

    /etc/httpd/conf.d/website.com.conf:
      apache.config:
        - config:
          - VirtualHost:
              this: '*:80'
              ServerName:
                -website.com
              ServerAlias:
                - www.website.com
                - dev.website.com
              ErrorLog: logs/website.com-error_log
              CustomLog: logs/website.com-access_log combinded
              DocumentRoot: /var/www/vhosts/website.com
              Directory:
                this: /var/www/vhosts/website.com
                Order: Deny,Allow
                Deny from: all
                Allow from:
                  - 127.0.0.1
                  - 192.168.100.0/24
                Options:
                  - +Indexes
                  - FollowSymlinks
                AllowOverride: All
'''

from __future__ import with_statement, print_function

# Import python libs
import os.path

# Import salt libs
import salt.utils.cloud


def __virtual__():
    return 'apache.config' in __salt__


def _check_name(name):
    ret = {'name': name,
           'changes': {},
           'result': None,
           'comment': ''}
    if salt.utils.cloud.check_name(
        name, ' a-zA-Z0-9.,_/\[\]\(\)\<\>\'*+:-'  # pylint: disable=W1401
    ):
        ret['comment'] = 'Invalid characters in name.'
        ret['result'] = False
        return ret
    else:
        ret['result'] = True
        return ret


def configfile(name, config):
    ret = _check_name(str(config))
    configs = __salt__['apache.config'](name, config, edit=False)
    current_configs = ''
    if os.path.exists(name):
        with open(name) as config_file:
            current_configs = config_file.read()

    if configs == current_configs.strip():
        ret['result'] = True
        ret['comment'] = 'Configuration is up to date.'
        return ret
    elif __opts__['test']:
        ret['comment'] = 'Configuration will update.'
        ret['result'] = None
        return ret

    try:
        with open(name, 'w') as config_file:
            print(configs, file=config_file)
        ret['changes'] = {
            'old': current_configs,
            'new': configs
        }
        ret['result'] = True
        ret['comment'] = 'Successfully created configuration.'
    except Exception as exc:
        ret['result'] = False
        ret['comment'] = 'Failed to create apache configuration.'

    return ret
