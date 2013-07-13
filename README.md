snakewithus-server
==================

# Cilent methods

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

## startwithconfig
called by ui to start game

```json
{
    player_urls: [
        'url to snake client endpoint', ...
    ],
    local_player: true|false,
    width: 100,
    height: 100
}
```

### expected response

```json
{
    game state object
}
```

## uidotick
called by ui at tick

```json
{
    game_id: "unique-id-for-game",
    local_player_move: "n|w|s|e"
}
```

### expected response
```json
{
    game state object
}
```

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

