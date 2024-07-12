#!/usr/bin/env python

#   Copyright (C) 2012 STFC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
'''
    This is a simple script to check the status of the APEL messages
    on the filesystem.  It uses the python-dirq library.  If any messages
    are locked, it gives the option to remove the lock.
    @author: Will Rogers
'''

from __future__ import print_function
from future.builtins import input, next

import sys
import os
from dirq.queue import Queue
from dirq.QueueSimple import QueueSimple

try:
    from apel.db.loader.loader import QSCHEMA
except ImportError:
    print('The apel package must be in the PYTHONPATH.')
    print('Exiting.')
    sys.exit(1)


def check_dir(root):
    '''
    Check the directory for incoming, outgoing, reject
    or accept directories.  If they exist, check them for
    messages.
    '''
    print('\nStarting message status script.')
    print('Root directory: %s\n' % root)
    queues = []
    incoming = os.path.join(root, 'incoming')
    if os.path.isdir(incoming):
        queues.append(Queue(incoming, schema=QSCHEMA))
    outgoing = os.path.join(root, 'outgoing')
    # outgoing uses QueueSimple, not Queue
    if os.path.isdir(outgoing):
        queues.append(QueueSimple(outgoing))
    reject = os.path.join(root, 'reject')
    if os.path.isdir(reject):
        queues.append(Queue(reject, schema=QSCHEMA))
    accept = os.path.join(root, 'accept')
    if os.path.isdir(accept):
        queues.append(Queue(accept, schema=QSCHEMA))

    for q in queues:
        msgs, locked = check_queue(q)
        #check_empty_dirs(q)
        print('    Messages: %s' % msgs)
        print('    Locked:   %s\n' % locked)
        if locked > 0:
            question = 'Unlock %s messages?' % locked
            if ask_user(question):
                clear_locks(q)


def check_queue(q):
    '''
    Given a queue, check through all messages to
    see if any are locked.  Return <total>, <number locked>.
    '''
    print('Checking directory: %s' % q.path)
    locked = 0
    name = q.first()
    # loop until there are no messages left
    while name:
        if not q.lock(name):
            locked += 1
            name = next(q, None)
            continue
        else:
            q.unlock(name)
            name = next(q, None)

    return q.count(), locked

def check_empty_dirs(q):
    empty_dirs = []
    path = q.path
    print("Checking path %s " % path)
    for item in os.listdir(path):
        ipath = os.path.join(path, item)
        if os.path.isdir(ipath):
            print(item)
            if len(os.listdir(ipath)) == 0:
                #empty_dirs.append(ipath)
                os.rmdir(ipath)


    print(empty_dirs)




def clear_locks(q):
    '''
    Go through all messages and remove any locks.
    '''
    name = q.first()
    while name:
        if not q.lock(name):
            q.unlock(name)
            name = next(q, None)


def ask_user(question):
    '''
    Ask the user to confirm the specified yes/no question.
    '''
    while True:
        ans = input('%s (y/n) ' % question).lower()
        if ans == 'y':
            return True
        elif ans == 'n':
            return False
        else:
            print('Choose y or n:')
            continue


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: %s <path to messages directory>")
        sys.exit()

    if not os.path.isdir(sys.argv[1]):
        print('Directory %s does not exist. Exiting.' % sys.argv[1])
        sys.exit()

    check_dir(sys.argv[1])
