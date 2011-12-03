gip.py - a simple application for working with iOS Notes in an IMAP
mailbox via the command line. 

At present, only Gmail is supported.

Usage
=====

List all Notes
--------------
    $python gip.py --username <your-gmail-address> list
    ('1', 'Thu, 06 Jan 2011 18:15:14 -0800', 'Note 1')
    ('2', 'Sun, 17 Apr 2011 10:11:27 -0700', 'Note 2')
    ...
