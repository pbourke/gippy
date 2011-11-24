"""
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

def get_credentials():
    """Read credentials from command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    args = parser.parse_args()
    return (args.username, args.password)

# test 1 : list contents of Notes folder
# accept u/p on command line
(username, password) = get_credentials()

# connect to imap server
imap = imaplib.IMAP4_SSL('imap.gmail.com')
imap.login(username, password)

# grab a list the id, date and subject of messages in the Notes folder
imap.select("Notes")
(typ, msgnums) = imap.search(None, "All")

# print the id, date and subject to stdout
for mid in bytes.decode(msgnums[0]).split():
    typ, msgdata = imap.fetch(mid, '(RFC822)')    
    msg = bytes.decode(msgdata[0][1])
    em = email.message_from_string(msg)    
    print(mid, em['Date'], em['Subject'])

