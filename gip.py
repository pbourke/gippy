""" vim: ff=unix
Copyright 2011 Patrick Bourke

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import argparse
import imaplib
import pprint
import email
import email.message
import email.utils
import datetime
import time
import uuid
import os
import tempfile
import getpass

def get_args():
    """Parse and return command line arguments"""
    parser = argparse.ArgumentParser(description='Add and edit iOS Notes via your favourite editor')
    parser.add_argument('-u', '--username', help='IMAP server username - ie: example@gmail.com', required=True)
    parser.add_argument('-s', '--server', help='IMAP server hostname', default='imap.gmail.com')
    parser.add_argument('-p', '--port', help='IMAP server port. If omitted, the default port is used')
    parser.add_argument('-n', '--no-ssl', help='Do not use SSL. SSL is used by default', action='store_true')
    parser.add_argument('action', choices=['list', 'show', 'edit', 'add'], help='action to take')
    parser.add_argument('messageId', type=int, nargs='?', help='message ID to show or edit')

    args = parser.parse_args()

    if args.action in ['show', 'edit'] and args.messageId == None:
        exit("You must specify a messageId with %s" % (args.action,))

    password = getpass.getpass("Enter password for %s at %s: " % (args.username, args.server))

    if not password:
        exit("Must enter a password")

    args.password = password

    return args

def connect_to_imap_server(args):
    """Connect to the GMail IMAP server and return an imaplib.IMAP4 instance to
       work with the GMail server"""
    return _connect_to_imap_server(args.username, args.password, args.server, args.port, args.no_ssl)

def _connect_to_imap_server(username, password, server, port, no_ssl):
    if no_ssl:
        port_to_use = port if port else imaplib.IMAP4_PORT
        imap = imaplib.IMAP4(server, port_to_use)
    else:
        port_to_use = port if port else imaplib.IMAP4_SSL_PORT
        imap = imaplib.IMAP4_SSL(server, port_to_use)

    imap.login(username, password)
    imap.select("Notes")
    return imap

def fetch_message(imap, imap_msg_id):
    """Retrieve a message from IMAP and return it as an email object"""
    typ, msgdata = imap.fetch(imap_msg_id, '(RFC822)')    
    encoded_msg = msgdata[0][1]
    return email.message_from_string(encoded_msg)    

def show_note(args):
    """Display content of a single Note (specified by IMAP message ID)"""
    imap = connect_to_imap_server(args)

    msg = fetch_message(imap, args.messageId)
    print(msg.as_string())

def list_notes(args):
    """Print a list of Notes to standard output"""
    imap = connect_to_imap_server(args)
    
    (typ, msgnums) = imap.search(None, "All")
    
    for imap_id in msgnums[0].split():
        msg = fetch_message(imap, imap_id)
        print(imap_id, msg['Date'], msg['Subject'])

def now_in_rfc_format():
    """see http://stackoverflow.com/questions/3453177/convert-python-datetime-to-rfc-2822"""
    nowdt = datetime.datetime.now()
    nowtuple = nowdt.timetuple()
    nowtimestamp = time.mktime(nowtuple)
    return email.utils.formatdate(nowtimestamp)

def _save_note_to_server(imap, msg):
    """Send msg to server via open IMAP connection imap"""
    # todo: test the \\Seen flag below
    imap.append('Notes', '\\Seen', imaplib.Time2Internaldate(time.time()), str.encode(str(msg)))

def add_note(args):
    # create stub message and write it to temporary file
    new_note = email.message.Message()
    new_note['Subject'] = "Replace with subject"
    new_note.set_payload("Replace with body")

    msg = _edit_note(args.username, new_note)

    # imap append
    imap = connect_to_imap_server(args)
    _save_note_to_server(imap, msg)

def edit_note(args):
    # obtain existing note from imap
    imap = connect_to_imap_server(args)
    msg = fetch_message(imap, args.messageId)
    edited_msg = _edit_note(args.username, msg)

    # insert new message
    _save_note_to_server(imap, edited_msg)

    # remove old message
    imap.store(args.messageId, '+FLAGS', '\\Deleted')

def _set_header(src, tgt, key, default):
    """Sets tgt[key] to src[key] if key in src and is nonempty, else sets it to
    default"""
    if key in src and src[key]:
        tgt[key] = src[key]
    else:
        tgt[key] = default

def _edit_note(username, note_msg):
    """Open $EDITOR to edit note_msg"""
    # write out a temporary file containing the subject and body
    # of note_msg
    filename = ""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_note = email.message.Message()
        temp_note['Subject'] = note_msg['Subject']
        temp_note.set_payload(note_msg.get_payload())
        f.write(temp_note.as_string())
        filename = f.name

    if len(filename) == 0:
        exit("Couldn't create temporary file")

    # launch $EDITOR against temporary file
    edit_cmd = "vi"
    if 'EDITOR' in os.environ:
        edit_cmd = os.environ['EDITOR']        

    os.system("%s %s" % (edit_cmd, filename))

    # read the edited message and remove the temporary file
    edited_message = ""
    with open(filename) as f:
        edited_message = f.read()

    os.remove(filename)

    if len(edited_message.strip()) == 0:
        exit("The edited note was empty - nothing to do!")

    # return a new message consisting of the edited message merged
    # with headers from the input message 
    now = now_in_rfc_format() 

    msg = email.message_from_string(edited_message)
    if 'Subject' not in msg or not msg['Subject']:
        msg['Subject'] = "Note"

    msg['From'] = username
    msg['To'] = username
    msg['Content-Type'] = "text/html; charset=utf-8"
    msg['Date'] = now    
    _set_header(note_msg, msg, 'X-Uniform-Type-Identifier', 'com.apple.mail-note')
    _set_header(note_msg, msg, 'X-Mail-Created-Date', now)
    _set_header(note_msg, msg, 'X-Universally-Unique-Identifier', str(uuid.uuid4()).upper())

    return msg

if __name__ == "__main__":
    args = get_args()
    if args.action == 'list':
        list_notes(args)
    elif args.action == 'show':
        show_note(args)
    elif args.action == 'add':
        add_note(args)
    elif args.action == 'edit':
        edit_note(args)

