var Snake = snakewithus.Snake = function(config_data) {
  this.id = config_data.id;
  this.last_move = null;
  this.name = config_data.name;
  this.facing = null,
  this.status = snakewithus.STATUS.ALIVE;
  this.message = '';
  this.points = { };
  this.color = 'rgba('+this.generateColor().join(',')+',1)';
};

Snake.prototype.generateColor = function() {
  var c = [ ];
  for (var i=0; i<3; i++) { c.push(Math.floor(Math.random()*256)); }
  return c;
};

