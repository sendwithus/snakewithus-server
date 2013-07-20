$(function() {
  var canvas = document.getElementById('canvas');
  var ctx = canvas.getContext('2d');

  var board = new snakewithus.Board(ctx, canvas);

  // HELPERS
  var pollTimeout = null;

  // COMPONENTS
  var $canvas          = $(canvas);
  var $newGameButton   = $('#create-game');
  var $startGameButton = $('#start-game');
  var $joinGameButton  = $('#join-game');
  var $fetchGameButton = $('#fetch-game');
  var $playerList      = $('#player-list');

  var $messageContainer = $('#messages');
  var $stateContainer = $('#state');

  var $gameIdContainers = $('.game-id');

  /** NEW GAME **/
  $newGameButton.on('click', function(e) {
    e.preventDefault();

    $.ajax({
      type: 'POST',
      contentType: 'application/json',
      dataType: 'json',
      url: '/game',
      data: JSON.stringify({
        width: 30,
        height: 20,
        local_player: false
      })
    }).done(function(gameState) {
      $gameIdContainers.text(gameState.id);
      board.init(gameState, updateUI);
      console.log('Initialized board:', board);
      $messageContainer.text('Waiting for players...');

      // WAIT FOR PLAYERS TO JOIN
      pollTimeout = setInterval(fetchGameState, 800);
      $newGameButton.hide();
      $canvas.fadeIn(400, function() {
        $fetchGameButton.fadeIn(400);
        $joinGameButton.fadeIn(400);
        $startGameButton.fadeIn(400);
      });
    });
  });

  /** START GAME **/
  $startGameButton.on('click', function(e) {
    e.preventDefault();

    // STOP POLLING FOR PLAYERS
    clearTimeout(pollTimeout);

    $.ajax({
      type: 'PUT',
      contentType: 'application/json',
      dataType: 'json',
      url: '/game.start/'+board.getGameId(),
      data: JSON.stringify({
        local_player: false,
        width: board.dimensions[0],
        height: board.dimensions[1]
      })
    }).done(function(gameState) {
      $joinGameButton.fadeOut(200);
      $startGameButton.fadeOut(200);
      board.update(gameState);
      board.kick();
      $messageContainer.text('Game has begun.');
    });
  });

  /** JOIN LOCAL GAME **/
  $joinGameButton.on('click', function(e) {
    $.ajax({
      type: 'PUT',
      contentType: 'application/json',
      dataType: 'json',
      url: '/game.addplayerurl/'+board.getGameId(),
      data: JSON.stringify({
        player_url: 'local_player'
      })
    }).done(function(player) {
      $joinGameButton.fadeOut(200);
      board.enableTestMode(player);
    });
  });

  var fetchGameState = function(print) {
    $.ajax({
      type: 'GET',
      dataType: 'json',
      url: '/game/'+board.getGameId()
    }).done(function(gameState) {
      if (print) {
        $stateContainer.show().html(
          'SNAKES:\n'+
          JSON.stringify(gameState.snakes, null, 2)+
          '\n\nBOARD:\n'+
          JSON.stringify(gameState.board, null, 2)
        );
      }

      // UPDATE BOARD
      board.update(gameState);
    });
  };

  var formatSnakePoints = function(points) {
    return '<small class="food-label">food:</small> '+points.food+'&nbsp;&nbsp;'+
           '<small class="life-label">life:</small> '+points.life+'&nbsp;&nbsp;'+
           '<small class="kill-label">kills:</small> '+points.kills;
  };

  var updateUI = function(gameState) {
    var html = '';
    for (var i=0; i<gameState.snakes.length; i++) {
      var snake = gameState.snakes[i];
      html += '<li>'+
        '<div class="ib snake-points tr pull-right">'+
          formatSnakePoints(snake.points)+
        '</div>'+
        '<h3'+
          ' data-player="'+snake.id+'"'+
          ' style="color:'+board.getSnake(snake.id).getColor()+'"'+
        '>* '+
          snake.name+':&nbsp;'+
        '</h3>'+
      '</li>';
    }
    $playerList.html(html);
  };

  $(window).on('resize', function(e) {
    // board.resize();
  });

  /** FETCH GAME STATE **/
  $fetchGameButton.on('click', function(e) {
    e.preventDefault();
    fetchGameState(true);
  });

  // COOL COLORS
  var $canvas = $(canvas);
  var $navbar = $('.navbar-inner');
  border = generateColor();
  var rgb = 'rgb('+border.join(',')+')';
  $canvas.css('border-color', rgb);
  $navbar.css('background', rgb);
});

sample_board_data = {
  id: "example-game-one",
  board: [
      [ [{type: "food", id: "f1"}], [], [], [{type: "snake", id: "snake_3"}], [{type: "snake", id: "snake_3"}], [{type: "snake", id: "snake_3"}], [{type: "snake", id: "snake_3"}], [{type: "snake", id: "snake_3"}], [], [] ],
      [ [], [{type: "food", id: "f2"}], [], [], [], [], [], [{type: "snake", id: "snake_3"}], [], [] ],
      [ [], [], [{type: "food", id: "f3"}], [], [], [], [], [{type: "snake_head", id: "snake_3"}], [], [] ],
      [ [], [], [], [{type: "food", id: "f4"}], [], [], [], [], [], [] ],
      [ [{type: "snake_head", id: "snake_1"}], [], [], [], [{type: "food", id: "f5"}], [], [], [], [], [] ],
      [ [{type: "snake", id: "snake_1"}], [], [], [], [], [{type: "food", id: "f6"}], [], [], [], [] ],
      [ [{type: "snake", id: "snake_1"}], [], [], [], [], [], [{type: "food", id: "f7"}], [], [], [] ],
      [ [{type: "snake", id: "snake_1"}], [], [], [], [], [], [], [{type: "food", id: "f8"}], [], [] ],
      [ [{type: "snake", id: "snake_1"}], [], [], [], [], [], [], [], [{type: "food", id: "f9"}], [] ],
      [ [{type: "snake", id: "snake_1"}], [], [], [], [], [], [], [], [], [{type: "food", id: "f0"}] ]
  ],
  snakes: [
    {
      id: "snake_1",
      last_move: "n",
      name: "Snake One",
      facing: "n",
      status: "alive",
      message: "I AM FUCKING SNAKE ONE",
      points: {
          kills: 10,
          food: 3
      }
    }, {
      id: "snake_2",
      last_move: "w",
      name: "Snake Two",
      facing: "w",
      status: "dead",
      message: "I am dead because I suck",
      points: {
          kills: 0,
          food: 0
      }
    }, {
      id: "snake_3",
      last_move: "s",
      name: "Snake Three",
      facing: "s",
      status: "alive",
      message: "Bitchin'",
      points: {
          kills: 1,
          food: 2
      }
    }
  ],
  turn_num: 0
};
