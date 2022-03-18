# README
Basic mikrotik backups

## You should have a backup user on your mikrotiks with appropriate permissions

```
/user group add name=backups policy=local,ssh,read,write,policy,test,password,sniff,sensitive,api,romon
/user add disabled=no name=backups group=backups password=<something secret>
```

## docker
docker-compose up -d

## Setup manually

```
pyenv exec pip3 install --user -r app/requirements.txt
```

Create the config file. Use the example and edit to suit

```
cp example.yaml devices.yaml
```
