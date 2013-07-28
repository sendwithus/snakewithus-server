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
  this.isStarted = false;
  this.lastTick = 0;
};

Board.prototype.resize = function() {
  var $board = $(this.canvas).closest('.board');

  var width  = $board.innerWidth()-60;
  var height = $(window).height()-160;

  var size1 = Math.ceil(width / this.dimensions[0]);
  var size2 = Math.ceil(height / this.dimensions[1]);

  this.SQUARE_SIZE = Math.min(size1, size2);

  this.canvas.width  = this.SQUARE_SIZE * this.dimensions[0];
  this.canvas.height = this.SQUARE_SIZE * this.dimensions[1];
};

Board.prototype.init = function(gameState, updateCallback) {
  this.updateCallback = updateCallback;
  this.gameState = gameState;
  this.dimensions = this.getBoardDimensions(this.gameState.board);
  this.update(gameState);
  this.resize();
};

Board.prototype.getGameId = function() {
  return this.gameState.id;
};

Board.prototype.isGameOver = function() {
  return this.gameState.game_over;
};

Board.prototype.kick = function() {
  this.isStarted = true;

  // DON'T KICK IF EXPECTING LOCAL INPUT
  if (this.testPlayer) { return; }

  this.tick();
};

Board.prototype.tick = function() {
  var that = this;

  this.yell(false, function() {
    var soonestNextTick = that.lastTick + snakewithus.MOVE_DELTA;
    var delta = soonestNextTick - Date.now();

    // Keep above 0
    delta = Math.max(0, delta);

    setTimeout(function() {
      that.tick.call(that);
      that.lastTick = Date.now();
    }, delta);
  });
};

Board.prototype.beginAnimation = function() {
  var that = this;
  this.animate();
  this.animationLoop = setInterval(function() {
    that.animate.call(that);
  }, 300);
};

Board.prototype.animate = function() {
  var boardData = this.gameState.board;
  for (var y=0; y<boardData.length; y++) {
    var row = boardData[y];
    for (var x=0; x<row.length; x++) {
      var square = row[x];
      var color = generateColor();
      color = makeNonGray(color, 150);
      var colorStr = 'rgb('+color.join(',')+')';
      this.fillSquare(x, y, colorStr);
    }
  }
};

Board.prototype.yell = function(localPlayerMove, callback) {
  if (!this.isStarted || this.isGameOver()) { return; }
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
    if (typeof callback === 'function') {
      callback();
    }
  });
};

Board.prototype.enableTestMode = function(testPlayer) {
  this.testPlayer = testPlayer || false;

  var that = this;
  $('body').on('keydown', function(e) {
    that.localMove(e);
  });
};

Board.prototype.localMove = function(e) {
  if (!this.testPlayer) { return; }

  key = e.keyCode;
  if (key === snakewithus.KEYS.UP) {
    e.preventDefault();
    this.yell(snakewithus.DIRECTIONS.NORTH);
  } else if (key === snakewithus.KEYS.DOWN) {
    e.preventDefault();
    this.yell(snakewithus.DIRECTIONS.SOUTH);
  } else if (key === snakewithus.KEYS.LEFT) {
    e.preventDefault();
    this.yell(snakewithus.DIRECTIONS.WEST);
  } else if (key === snakewithus.KEYS.RIGHT) {
    e.preventDefault();
    this.yell(snakewithus.DIRECTIONS.EAST);
  }
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

  if (typeof this.updateCallback === 'function') {
    this.updateCallback(gameState);
  }

  if (this.isGameOver()) {
    clearInterval(this.loop);
    this.beginAnimation();
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

  this.fillSquare(x, y, snakewithus.COLORS.EMPTY);
  if (!square_obj) {
    // Nothing
  } else if (square_obj.type === snakewithus.SQUARE_TYPES.SNAKE) {
    snake = this.getSnake(square_obj.id);
    this.fillSquare(x, y, snake.getColor());
  } else if (square_obj.type === snakewithus.SQUARE_TYPES.SNAKE_HEAD) {
    snake = this.getSnake(square_obj.id);
    this.fillSquare(x, y, snake.getHeadColor());
  } else if (square_obj.type === snakewithus.SQUARE_TYPES.FOOD) {
    this.fillCircle(x, y, snakewithus.COLORS.FOOD);
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
  var xStart = x * this.SQUARE_SIZE;
  var yStart = y * this.SQUARE_SIZE;

  this.ctx.beginPath();
  this.ctx.rect(
    xStart + snakewithus.SQUARE_PADDING,
    yStart + snakewithus.SQUARE_PADDING,
    this.SQUARE_SIZE - snakewithus.SQUARE_PADDING * 2,
    this.SQUARE_SIZE - snakewithus.SQUARE_PADDING * 2
  );
  this.ctx.fillStyle = color;
  this.ctx.fill();
};

Board.prototype.fillCircle = function(x, y, color) {
  var halfSquare = Math.round(this.SQUARE_SIZE / 2);
  var xCenter = x * this.SQUARE_SIZE + halfSquare;
  var yCenter = y * this.SQUARE_SIZE + halfSquare;
  var radius = this.SQUARE_SIZE/2 * snakewithus.FOOD_SIZE;

  this.ctx.beginPath();
  this.ctx.arc(xCenter, yCenter, radius, 0, 2 * Math.PI);
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