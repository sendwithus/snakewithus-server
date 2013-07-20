var Snake = snakewithus.Snake = function(config_data) {
  this.id = config_data.id;
  this.last_move = null;
  this.name = config_data.name;
  this.facing = null,
  this.status = snakewithus.STATUS.ALIVE;
  this.message = '';
  this.points = { };
  this.color = generateColor();
};

Snake.prototype.getColor = function() {
  return 'rgba('+this.color.join(',')+','+snakewithus.BODY_OPACITY+')';
};

Snake.prototype.getHeadColor = function() {
  return 'rgba('+this.color.join(',')+','+snakewithus.BODY_OPACITY+')';
};
