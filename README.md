SNAKEWITHUS
===========

What you need to know
---------------------

This isn't any old game of snake.  Here are some differences.

* It's multiplayer.
* You control your snake by writing AI
* It's RESTful


What you need to do
-------------------

The snakewithus server will POST to 5 different endpoints that your snake has to respond to.

1. /register

A request is made to this endpoint once when you register.  Expected return data:

```json
{
    name: "Franky",
    head_img_url: "path/to/your/snake/head"
}
```

2. /start

A request is made to this endpoint when the game starts.  You can do stuff here if you want.

3. /end

A request is made here when your snake dies.  Do stuff.

4. /tick

The server POSTs the game board state to your snake every tick.  Expected return data:

```json

{
    move: "n|e|s|w",
    message: "troll comment"
}

```

How to register your snake
--------------------------

Create a new game by going to snakewithus-server.herokuapp.com and clicking "NEW GAME".  It will create a game instance for you.

curl -XPUT 'http://snakewithus-server.herokuapp.com/game.addplayerurl/game-name' -d '{ "player_url": "http://yourserver.com" }' -H "content-type: application/json"    




snakewithus-server
==================

# Client methods
clients must implement the below REST methods

## register

called when the client joins a new game

request body

```json
{
    game_id: "unique-id-for-game",
    client_id: "unique-id-server-generated-for-client",
    board: {
        width: "width",
        height: "height",
        num_players: 0
    }
}
```

expected response

```json
{
    name: "name of the snake",
    head_img_url: "(optional) url to 10x10 image for snake head"
}
```

## start
called at the start of a game

request body

```json
{
    game_id: "unique-id-for-game"
}
```

expected response

```json
{}
```

## end
called at the end of a game

request body

```json
{
    game_id: "unique-id-for-game"
}
```

expected response

```json
{}
```

## tick
called at every game tick

```json
{
    Game state object (see below)
}
```

expected response

```json
{
    move: "n|e|s|w",
    message: ""
}
```
# Object Structures

## Game state object
```json
{
    id: "unique-id-for-game",
    board: [
        [
            [{}, {}, ...], [{}, {}, ...], [{}, {}, ...], [{}, {}, ...], ... // Game square objects (see below)
            [{}, {}, ...], [{}, {}, ...], [{}, {}, ...], [{}, {}, ...], ...
            [{}, {}, ...], [{}, {}, ...], [{}, {}, ...], [{}, {}, ...], ...
        ], ...
    ],
    snakes: [
        {
            id: "id of snake",
            last_move: "",
            name: "name of snake",
            facing: "n|e|s|w",
            status: "dead|alive",
            message: "",
            points: {
                kills: 0,
                food: 0,
            }
        }, ...
    ],
    turn_num: 0
}
```

## Game square object

```json
{
    type: "snake|food|snake_head",
    id: "snake id or null"
}
```

