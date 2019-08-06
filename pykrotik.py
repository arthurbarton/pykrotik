#!/usr/bin/env python3
import paramiko
import os
import datetime
import configparser

# read config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# housekeeping
backuproot = config['DEFAULT']['backuproot']
debug = config['DEFAULT'].getboolean('debug')
today = (datetime.date.today()).strftime("%Y%m%d")
backuppath = str(backuproot) + '/' + today
if not os.path.exists(backuppath):
    os.makedirs(backuppath)

# debug on/off from ini
if debug:
    import logging
    logging.basicConfig(level=logging.DEBUG)


# this is where the work happens
def remoterun(name, ip, port, user, passw):
    if debug:
        print("Connecting to", name, ip, port, "as", user)
    # ssh client + connect it
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passw,allow_agent=False,look_for_keys=False)

    # export
    stdin,stdout,stderr = client.exec_command('/export compact file=export.rsc')
    if stderr:
        err = stderr.read().decode('utf-8')
        if debug:
            print("Export errors: " + err)

    # backup
    stdin,stdout,stderr = client.exec_command('/system backup save name=today')
    if stderr:
        err = stderr.read().decode('utf-8')
        if debug:
            print("Export errors: " + err)

    # download the files
    sftp_client=client.open_sftp()
    sftp_client.get('export.rsc',backuppath + '/' + name + '-export.rsc')
    sftp_client.get('today.backup',backuppath + '/' + name + '-today.backup')

    client.close()

# loop over the config file
for key in config:
    if not 'DEFAULT' in key:
        name = str(key)
        ip = config[key]['ip']
        # allow port to be set/not set
        if config[key].get('port'):
            port = int(config[key]['port'])
        elif config['DEFAULT'].get('port'):
            port = int(config['DEFAULT']['port'])
        else:
            port = 22
        u = config[key]['username']
        p = config[key]['password']

        remoterun(name, ip, port, u, p)

exit(0)
