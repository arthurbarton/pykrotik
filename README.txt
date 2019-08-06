# README
Basic mikrotik backups

## You should have a backup user on your mikrotiks with appropriate permissions

```
/user group add name=backups policy=local,ssh,read,write,policy,test,password,sniff,sensitive,api,romon
/user add disabled=no name=backups group=backups password=<something secret>
```

## Setup the repo

You need to install the [paramiko/paramiko](https://github.com/paramiko/paramiko) library

```
pip3 install --user paramiko
```

Create the config file. Use the example and edit to suit

```
cp example.ini config.ini
```
