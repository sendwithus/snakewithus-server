window.snakewithus = {
  MOVE_DELTA: 1000,
  SQUARE_PADDING: 2,
  FOOD_PROBABILITY: 0.005,
  HEAD_OPACITY: 1,
  BODY_OPACITY: 0.5,
  SQUARE_TYPES: {
    SNAKE: 'snake',
    SNAKE_HEAD: 'snake_head',
    FOOD: 'food'
  },
  DIRECTIONS: {
    NORTH: 'n',
    EAST: 'e',
    SOUTH: 's',
    WEST: 'w'
  },
  STATUS: {
    ALIVE: 'alive',
    DEAD: 'dead'
  },
  COLORS: {
    FOOD: '#F79E53',
    EMPTY: '#444'
  },
  MAX_COLOR: 230,
  MIN_COLOR: 150,
  BORDER_CHANGE: 4,
  KEYS: {
    UP: 38,
    DOWN: 40,
    LEFT: 37,
    RIGHT: 39
  }
};

window.generateColor = function() {
  var color = [ ];
  for (var i=0; i<3; i++) {
    var c = Math.min(
      Math.max(
        snakewithus.MIN_COLOR, Math.floor(Math.random()*256
      )
    ), snakewithus.MAX_COLOR);
    color.push(c);
  }
  return color;
};

window.getURLParameter = function (name, defaultValue) {
  var val = decodeURI(
    (RegExp(name + '=' + '(.+?)(&|$)').exec(location.search)||[,null])[1]
  );

  if (val === 'null') {
    val = defaultValue;
  }
  return val;
};
