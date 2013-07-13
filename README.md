snakewithus-server
==================

# Cilent methods

## register

called with the client joins a new game

### request body

```json
{
    game_id: "unique-id-for-game",
    client_id: "unique-id-server-generated-for-client",
}
```

### expected response

```json
{
    name: "name of the snake",
    head_img_url: "(optional) url to 10x10 image for snake head"
}
```

## start

called when a new game is started

### request body

```json
{
    game_id: "unique-id-for-game",
    board_size: {
        width: "width",
        height: "height"
    }
}
```

### expected response

```json
{}
```

## end
called at the end of a game

### request body

```json
{
    game_id: "unique-id-for-game"
}
```

### expected response

```json
{}
```

## tick
called at every game tick

```json
{
    game_id: "unique-id-for-game",
    game_board: [
        [
            [{}, {}, ...]
        ], ...
    ],
    snake_status: {
        snake_id: "status (dead/alive)"
    },
    tick_ts: "timestamp for tick"
}
```

### expected response

```json
{}
```

