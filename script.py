#! /usr/bin/env python
# -*- coding: utf-8 -*
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
import os
import sys
from datetime import datetime

# This access token will be used to access
# Please use your own token. More link: //www.dropbox.com/developers/documentation/python#tutorial
TOKEN = '****'


def backup(LOCALFILE, BACKUPPATH):
    try:
        with open(LOCALFILE, 'rb') as f:
            print("Uploading " + LOCALFILE + " to Dropbox as " + BACKUPPATH + "...")
            try:
                dbx.files_upload(f.read(), BACKUPPATH, mode=WriteMode('overwrite'), autorename=True)
            except ApiError as err:
                # This checks for the specific error where a user doesn't have
                # enough Dropbox space quota to upload this file
                if (err.error.is_path() and
                        err.error.get_path().error.is_insufficient_space()):
                    sys.exit("ERROR: Cannot back up; insufficient space.")
                elif err.user_message_text:
                    print(err.user_message_text)
                    sys.exit()
                else:
                    print(err)
                    sys.exit()
    except FileNotFoundError:
        sys.exit("ERROR: A dump-file is requested but doesn’t exist.")


if __name__ == '__main__':
    db_name = sys.argv[1]
    time = (datetime.now())
    time = time.strftime(":%d.%m.%Y%I:%M")
    # Bash command to dump
    os.system(
        'pg_dump --host localhost --port 5432 --username postgres --no-password  --format plain --verbose --file $PWD/' +
        db_name + time + '.sql ' + db_name)
    LOCALFILE = db_name + time + '.sql'
    BACKUPPATH = '/' + db_name + time + '-dump-backup.sql'
    # Check for an access token
    if (len(TOKEN) == 0):
        sys.exit("ERROR: Looks like you didn't add your access token.")
    # Check that the access token is valid
    print("Creating a Dropbox object...")
    dbx = dropbox.Dropbox(TOKEN)
    try:
        dbx.users_get_current_account()
    except AuthError as err:
        sys.exit("ERROR: Invalid access token; try re-generating an access token.")
    backup(LOCALFILE, BACKUPPATH)
    try:
        os.remove(LOCALFILE)
        print("Local file removed!")
    except FileNotFoundError:
        print("ERROR: file  is requested but doesn’t exist.")
