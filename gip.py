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

def get_args():
    """Read credentials from command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    parser.add_argument('action')
    parser.add_argument('-m', '--messageId', required=False)
    args = parser.parse_args()
    return args

def connect_to_imap_server(args):
    """Connect to the GMail IMAP server and return an imaplib.IMAP4 instance to
       work with the GMail server"""
    return _connect_to_imap_server(args.username, args.password)

def _connect_to_imap_server(username, password):
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    imap.login(username, password)
    imap.select("Notes")
    return imap

def fetch_message(imap, imap_msg_id):
    """Retrieve a message from IMAP and return it as an email object"""
    typ, msgdata = imap.fetch(imap_msg_id, '(RFC822)')    
    encoded_msg = bytes.decode(msgdata[0][1])
    return email.message_from_string(encoded_msg)    

def show_note(args):
    """Display content of a single Note (specified by IMAP message ID)"""
    imap = connect_to_imap_server(args)

    msg = fetch_message(imap, args.messageId)
    print(msg)

def list_notes(args):
    """Print a list of Notes to standard output"""
    imap = connect_to_imap_server(args)
    
    (typ, msgnums) = imap.search(None, "All")
    
    # print the id, date and subject to stdout
    for imap_id in bytes.decode(msgnums[0]).split():
        msg = fetch_message(imap, imap_id)
        print(imap_id, msg['Date'], msg['Subject'])

def now_in_rfc_format():
    """http://stackoverflow.com/questions/3453177/convert-python-datetime-to-rfc-2822"""
    nowdt = datetime.datetime.now()
    nowtuple = nowdt.timetuple()
    nowtimestamp = time.mktime(nowtuple)
    return email.utils.formatdate(nowtimestamp)

def add_test_note(args):
#    filename = ""
#    with tempfile.TemporaryFile() as f:
#        f.write("Subject: edit me\r\n")
#        filename = f.name
#
#    # launch $EDITOR to create the note
#    edit_cmd = "vi"
#    if 'EDITOR' in os.environ:
#        edit_cmd = os.environ['EDITOR']        
#
#    os.system(edit_cmd + " " + filename)

    # format message
    now = now_in_rfc_format() 

    msg = email.message.Message()
    msg['Subject'] = "Another test!"
    msg['From'] = args.username
    msg['To'] = args.username
    msg['Content-Type'] = "text/html; charset=utf-8"
    msg['X-Uniform-Type-Identifier'] = "com.apple.mail-note"
    msg['X-Mail-Created-Date'] = now
    msg['Date'] = now
    msg['X-Universally-Unique-Identifier'] = str(uuid.uuid4()).upper()
    # todo: read in tempfile and set its content as payload
    msg.set_payload("<div>This is a test from Python</div><div><b>bold</b></div><div><ul><li>item 1</li><li>item 2</li></div>")

    # imap append
    imap = connect_to_imap_server(args)
    imap.append('Notes', '', imaplib.Time2Internaldate(time.time()), str.encode(str(msg)))

def edit_test_note(args):
# obtain existing note from imap
# del Subject, Date, Message-Id
# add new Subject, Date
# change body 
# insert new message
# remove old message - imap.store("16", '+FLAGS', '\\Deleted')
    pass

if __name__ == "__main__":
    args = get_args()
    if args.action == 'list':
        list_notes(args)
    elif args.action == 'show':
        show_note(args)
    elif args.action == 'test-add':
        add_test_note(args)

