# Exterra Group - mobiglas

A Discord bot for integrating with Exterra Group's SCOrgSite.
mobiglas is a Discord bot written in Python 3.6.7 built with [discord.py v1.2.3](https://github.com/Rapptz/discord.py) and [meowth.py](https://github.com/FoglyOgly/Meowth).

## mobiglas v1 Features
- Integration with Exterra Group's [SCOrgSite](Insert_Link_HERE). Includes the ability to sync members/roles.
- For fun commands: e.g. !gib
- Motion/Voting System for Board Members
- Raid Coordination System for Members
- Retrieve Dossier of any Member


## Development

#### Dependencies

##### Python 
Minimum: `Python 3.6.1+` Recommended: `Python 3.6.7`

##### curl-config
Debian `sudo apt install libcurl4-openssl-dev libssl-dev`

Yum `yum install libcurl-devel`

OSX `PYCURL_SSL_LIBRARY=openssl LDFLAGS="-L/usr/local/opt/openssl/lib" CPPFLAGS="-I/usr/local/opt/openssl/include" pip install --no-cache-dir pycurl` 

##### Git
To clone the files from our repository or your own forked repository on GitHub, you will to have `git` installed.

##### Required Python Packages
`pip install -r requirements.txt --upgrade`

## Deployment

#### Dependencies

##### Docker

Build Docker Volume `docker volume create mobiglas-vol`

Build Docker Container `docker build --tag mobiglas .`

Run mobiglas `docker run -v mobiglas-vol:/build -i -d #IMAGE_ID`


#### Credits
mobiglas is an adaption of the Meowth raid bot by [FoglyOgly](https://github.com/FoglyOgly/Meowth).