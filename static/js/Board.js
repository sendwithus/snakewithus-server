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
};

Board.prototype.kick = function() {
  var that = this;
  this.loop = setInterval( function() {
  // this.loop = setTimeout( function() {
    console.log('Yelling...');
    that.yell( function(gameState) {
      that.update(gameState);
    });
  }, snakewithus.MOVE_DELTA);
};

Board.prototype.yell = function(callback) {
  var data = {
    game_id: this.gameState.id,
    local_player_move: false
  };
  console.log('TICK', data);

  $.ajax({
    type: 'POST',
    contentType: 'application/json',
    dataType: 'json',
    url: 'uidotick',
    data: JSON.stringify(data)
  }).done(function(gameState) {
    callback(gameState);
  });
};

Board.prototype.init = function(gameState) {
  this.dimensions = this.getBoardDimensions(gameState.board);
  this.canvas.width = snakewithus.SQUARE_SIZE * this.dimensions[0];
  this.canvas.height = snakewithus.SQUARE_SIZE * this.dimensions[1];
};

Board.prototype.update = function(gameState) {
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