snakewithus-server
==================

# Client methods

## register

called with the client joins a new game

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
    game state object
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
            [{}, {}, ...], [{}, {}, ...], [{}, {}, ...], [{}, {}, ...], ...
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
square: {
    type: "snake|food|snake_head",
    id: "snake id or null"
}
```

