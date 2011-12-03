gip.py - a simple application for working with iOS Notes in an IMAP
mailbox via the command line. 

At present, only Gmail is supported.

Usage
=====

List all notes
--------------
**list** displays a summary of the notes on the server   
    $python gip.py --username <your-gmail-address> list
    Enter password for <your-gmail-address>:
    ('1', 'Thu, 06 Jan 2011 18:15:14 -0800', 'Note 1')
    ('2', 'Sun, 17 Apr 2011 10:11:27 -0700', 'Note 2')
    ...

Show a note
-----------
**show** displays the full contents of a single note
    $python gip.py --username <your-gmail-address> show 1
    Enter password for <your-gmail-address>:
    Subject: Note 1
    From: You Name <your-gmail-address>
    X-Universally-Unique-Identifier: E3861089-EAD5-4DB0-BBDB-E4138ED2DD48
    Content-Type: text/html;
            charset=utf-8
    X-Uniform-Type-Identifier: com.apple.mail-note
    Message-Id: <someId>
    Date: Thu, 06 Jan 2011 18:15:14 -0800
    X-Mail-Created-Date: Tue, 04 Jan 2011 10:51:19 -0800
    Content-Transfer-Encoding: 7bit
    Mime-Version: 1.0 (iPhone Mail 8C148a)
    
    <div>Note 1</div>

Edit a note
-----------
**edit** launches $EDITOR to upload a new version of an existing note. Behind the scenes, the old note is removed and the new one appended.
    $python gip.py --username <your-gmail-address> show 1
    Enter password for <your-gmail-address>:

Add a note
----------
**add** launches $EDITOR to append a new note
    $python gip.py --username <your-gmail-address> add
    Enter password for <your-gmail-address>:
