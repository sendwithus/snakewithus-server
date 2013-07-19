/**
 *  Main game board class
 */
var Board = window.snakewithus.Board = function(ctx, canvas) {
  this.ctx = ctx;
  this.canvas = canvas;
  this.dimensions = null;
  this.snakeCache = { };
  this.gameState = {
    id: 'None',
    board: [ ],
    snakes: [ ],
    turn: 0
  };

  this.testPlayer = false;
};

Board.prototype.init = function(gameState) {
  this.gameState = gameState;
  this.dimensions = this.getBoardDimensions(this.gameState.board);
  this.canvas.width = snakewithus.SQUARE_SIZE * this.dimensions[0];
  this.canvas.height = snakewithus.SQUARE_SIZE * this.dimensions[1];

  this.update(gameState);
};

Board.prototype.getGameId = function() {
  return this.gameState.id;
};

Board.prototype.kick = function() {
  // DON'T KICK IF EXPECTING LOCAL INPUT
  if (this.testPlayer) { return; }

  var that = this;
  this.loop = setInterval(
    this.yell,
    snakewithus.MOVE_DELTA
  );
};

Board.prototype.yell = function(localPlayerMove) {
  var data = {
    game_id: this.gameState.id
  };

  if (localPlayerMove) {
    data.local_player_move = {
      player_id: this.testPlayer.id,
      data: {
        move: localPlayerMove
      }
    };
  }

  var that = this;

  $.ajax({
    type: 'PUT',
    contentType: 'application/json',
    dataType: 'json',
    url: '/game.tick/'+this.getGameId(),
    data: JSON.stringify(data)
  }).done(function(gameState) {
    that.update(gameState);
  });
};

Board.prototype.enableTestMode = function(testPlayer) {
  this.testPlayer = testPlayer || false;

  var that = this;
  $(window).on('keydown', function(e) {
    that.localMove(e.keyCode);
  });
};

Board.prototype.localMove = function(key) {
  if (!this.testPlayer) { return; }

  if (key === snakewithus.KEYS.UP) {
    this.yell(snakewithus.DIRECTIONS.NORTH);
  } else if (key === snakewithus.KEYS.DOWN) {
    this.yell(snakewithus.DIRECTIONS.SOUTH);
  } else if (key === snakewithus.KEYS.LEFT) {
    this.yell(snakewithus.DIRECTIONS.WEST);
  } else if (key === snakewithus.KEYS.RIGHT) {
    this.yell(snakewithus.DIRECTIONS.EAST);
  }
  console.log(key);
};

Board.prototype.update = function(gameState) {
  console.log('Updated game state.');
  this.gameState = gameState;

  this.canvas.width = this.canvas.width;

  var boardData = gameState.board;

  for (var y=0; y<boardData.length; y++) {
    var row = boardData[y];
    for (var x=0; x<row.length; x++) {
      var square = row[x];
      this.drawSquare(x, y, square);
    }
  }
};

Board.prototype.drawSquare = function(x, y, square) {
  if (square.length > 1) {
    console.error(
      'ERROR: More than one object returned at square', x, y
    );
  }

  var snake;
  var square_obj = square[0];

  if (!square_obj) { // EMPTY SQUARE
    this.fillSquare(x, y, snakewithus.COLORS.EMPTY);
  } else if (square_obj.type === snakewithus.SQUARE_TYPES.SNAKE) {
    snake = this.getSnake(square_obj.id);
    this.fillSquare(x, y, snake.color);
  } else if (square_obj.type === snakewithus.SQUARE_TYPES.SNAKE_HEAD) {
    snake = this.getSnake(square_obj.id);
    this.fillSquare(x, y, snake.color);
  } else if (square_obj.type === snakewithus.SQUARE_TYPES.FOOD) {
    this.fillSquare(x, y, snakewithus.COLORS.FOOD);
  } else {
    console.error('INVALID SQUARE TYPE', square_obj.type);
  }
};

Board.prototype.getSnake = function(id) {
  var snake_config = null;
  for (var i=0; i<this.gameState.snakes.length; i++) {
    var config = this.gameState.snakes[i];
    if (config.id === id) {
      snake_config = config;
    }
  }
  var snake = this.snakeCache[snake_config.id];

  if (!snake) {
    snake = this.snakeCache[snake_config.id] = new Snake(snake_config);
  }

  return snake;
};

Board.prototype.getBoardDimensions = function(board) {
  var height = board.length;
  var width = 0;

  if (board[0]) {
    width = board[0].length;
  }

  return [ width, height ];
};

Board.prototype.fillSquare = function(x, y, color) {
  var xStart = x * snakewithus.SQUARE_SIZE;
  var yStart = y * snakewithus.SQUARE_SIZE;

  this.ctx.beginPath();
  this.ctx.rect(
    xStart + snakewithus.SQUARE_PADDING,
    yStart + snakewithus.SQUARE_PADDING,
    snakewithus.SQUARE_SIZE - snakewithus.SQUARE_PADDING * 2,
    snakewithus.SQUARE_SIZE - snakewithus.SQUARE_PADDING * 2
  );
  this.ctx.fillStyle = color;
  this.ctx.fill();
};

Board.prototype.shouldBeFood = function() {
  var luckyNumber = (1 / snakewithus.FOOD_PROBABILITY);
  var couldBeZero = Math.floor(Math.random()*luckyNumber);

  return !couldBeZero;
};

Board.prototype.genBoard = function(width, height) {
  var board = [ ];

  for (var y=0; y<height; y++) {
    var row = [ ];
    for (var x=0; x<width; x++) {
      var square = [ ];

      if (this.shouldBeFood()) {
        square.push({
          id: 'ntsir',
          type: snakewithus.SQUARE_TYPES.FOOD
        });
      }
      row.push(square);
    }
    board.push(row);
  }
  return board;
};