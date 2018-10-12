# duel_arena_server
Server for running bot matches in Gomoku.

Requires mongodb running locally.

## Mongodb installation for Ubuntu 14.04:
* `sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4`
* `echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list`
* `sudo apt-get update`
* `sudo apt-get install -y mongodb-org`
