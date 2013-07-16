$(function() {
  var canvas = document.getElementById('canvas');
  var ctx = canvas.getContext('2d');

  var board = new snakewithus.Board(ctx, canvas);

  // var test_board = board.genBoard(20, 20);
  // sample_board_data.board = test_board;

  // board.init(sample_board_data);

  var pollTimeout = null;

  var $newGameButton   = $('#create-game');
  var $startGameButton = $('#start-game');
  var $fetchGameButton = $('#fetch-game');

  var $gameIdContainer = $('#game-id');

  /** NEW GAME **/
  $newGameButton.on('click', function(e) {
    e.preventDefault();

    $.ajax({
      type: 'POST',
      contentType: 'application/json',
      dataType: 'json',
      url: '/game',
      data: JSON.stringify({
        width: 10,
        height: 10,
        local_player: false
      })
    }).done(function(gameState) {
      $gameIdContainer.text(gameState.id);
      board.init(gameState);
      console.log('Initialized board:', board);

      // WAIT FOR PLAYERS TO JOIN
      pollTimeout = setInterval(fetchGameState, 800);
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
      board.update(gameState);
      board.kick();
    });
  });

  var fetchGameState = function() {
    $.ajax({
      type: 'GET',
      dataType: 'json',
      url: '/game/'+board.getGameId()
    }).done(function(gameState) {
      board.update(gameState);
    });
  };

  /** FETCH GAME STATE **/
  $fetchGameButton.on('click', function(e) {
    e.preventDefault();
    fetchGameState();
  });
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
