#!/usr/bin/env python3
"""Backup a list of mikrotiks"""
import os
import sys
import datetime
import argparse
import logging
import paramiko
import yaml


def _do_paramiko_exec(pclient: paramiko.SSHClient, cmd: str) -> tuple():
    """Perform the exec on the P client - and cleanup

    Args:
        pclient (paramiko.SSHClient): Already established SSH Client
        cmd (str): the command to exec

    Returns:
        tuple (
            Success (bool): true if so
            STDIN, STDOUT, STDERR
        )
    """

    remote_cmd = pclient.exec_command(cmd)

    for stdp in remote_cmd:
        if stdp and not bool(stdp) and not stdp.closed():
            stdp.close()

    return (
        # pylint: disable=simplifiable-if-expression
        True if not any(c.isalpha() for c in remote_cmd[2].read().decode("utf-8")) else False,
        remote_cmd
    )

parser = argparse.ArgumentParser(description="Shoddy MikroTik backups")
parser.add_argument(
    "-v",
    "--verbose",
    required=False,
    default=False,
    action="store_true",
    help="Be verbose",
)
parser.add_argument(
    "-d",
    "--devices",
    required=False,
    type=str,
    default="devices.yaml",
    help="Path to devices.yaml",
)
parser.add_argument("-o", "--output", required=True, type=str, help="Output Directory")
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

if not os.path.isfile(args.devices):
    print("No devices.yaml file")
    sys.exit()

with open(args.devices) as yamlconf:
    config = yaml.safe_load(yamlconf)

if not os.path.isdir(args.output):
    print(f"Output path - {args.output} - does not exist. Creating it")
    os.makedirs(args.output)

today = (datetime.date.today()).strftime("%Y%m%d")
# loop over the config file
for device in config:
    remoteDevice = config[device]

    # ssh client + connect it
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        remoteDevice["ip"],
        port=remoteDevice["port"] if remoteDevice.get("port") else 22,
        username=remoteDevice["username"],
        password=remoteDevice["password"],
        allow_agent=False,
        look_for_keys=False,
    )

    for cmds in [f"/export compact file=export-{today}.rsc",
                f"/system backup save name=backup-{today}"]:
        success, res = _do_paramiko_exec(client, cmds)
        if not success and res[2] and args.verbose:
            print(f'Command - {cmds} - errors.\n{res[2]}')

    for files in [
        f"export-{today}.rsc",
        f"backup-{today}.backup"
    ]:
        sftp_client = client.open_sftp()
        sftp_client.get(files, f'{args.output}/{device}-{files}')
        sftp_client.close()

    client.close()

sys.exit(0)
