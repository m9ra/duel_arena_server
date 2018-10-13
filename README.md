# duel_arena_server
Server for running bot matches in Gomoku.

Requires mongodb running locally.

## Mongodb installation for Ubuntu 14.04:
* `sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4`
* `echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list`
* `sudo apt-get update`
* `sudo apt-get install -y mongodb-org`


## Network Communication
### Data Format
* TCP/IP messages
* payload: header of 4bytes + JSON message
* header determines byte length of the 'utf-8' encoded message
    * header is a 32bit integer with the most significant byte at the beginning  

### Communication Protocol
1\. player `my.name` connects to the arena (only one parallel TCP/IP connection is allowed for a single username)

<b>arena</b> <<< `{"username": "my.name"}`

2\. then the player waits for status confirmation by the arena

<b>arena</b> \>\>\> `{"status": "ok"}`

3\. the player still waits until arena recognizes them as a free player

<b>arena</b> \>\>\>  `{"event": "player_is_free"}`

4\. after that, player can request an opponent

<b>arena</b> <<< `{"event": "find_opponent"}`

5\. when opponent is found, arena notifies the player about game started (two consecutive games with switched colors will be played)

<b>arena</b> \>\>\>  `{"event": "starting_game", "against": "other.player.name"}`

6\. during the game, moves are requested as follows (the board situation is sent as move sequence from the start)

<b>arena</b> \>\>\>  `{"event": "get_move", "id": "1539438438.770872-98380", "board": {"_id": 15509, "_size": 15, "_win_length": 5, "_moves": [[5, 8], [4, 0], [9, 8], [13, 14]]}}`

7\. player is required to reply before the timeout (otherwise move is considered invalid), invalid move looses the board immediately

<b>arena</b> <<< `{"event": "make_move", "id": "1539438438.770872-98380", "x": 5, "y": 12}`

8\. after game ended, information about game result is sent 

<b>arena</b> \>\>\>  `{"event": "win", "board": {"_id": 15509, "_size": 15, "_win_length": 5, "_moves": [[5, 8], [4, 0], [9, 8], [13, 14], [5, 12], [14, 8], [9, 12], [12, 5], [14, 13], [5, 5], [14, 7], [5, 10], [13, 12], [10, 11], [12, 11], [13, 4], [10, 9], [10, 13], [11, 10]]}}`

9\. after two games played against the opponent, player is notified that their status is `free`

<b>arena</b> \>\>\>  `{"event": "player_is_free"}`

10\. at this point, the player can freely disconnect or find another opponent by sending

<b>arena</b> <<< `{"event": "find_opponent"}`