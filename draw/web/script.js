var scale = 4;
pixels = new Array(128);

var socket = new WebSocket("ws://192.168.1.12:5000");

onStart = function() {
    createCanvas(128 * scale, 32 * scale);
    outlineCanvas();

    for (var i =  0; i < pixels.length; i++)
    {
        pixels[i] = new Array(32);
    }

    play();
}

onMouseMove = function(x, y) {

    x = Math.floor(x / scale);
    y = Math.floor(y / scale);

    if (leftMouseDown) {
        pixels[x][y] = 1;
        socket.send(x + "," + y + ",1");
    }
    if (rightMouseDown) {
        pixels[x][y] = 0;
        socket.send(x + "," + y + ",0");
    }

}

onRender = function() {
    for (var i = 0; i < 128; i++)
    {
        for (var j = 0; j < 32; j++)
        {
            if(pixels[i][j] == 1)
                draw(new Rectangle(i * scale, j * scale, scale, scale));
        }
    }

    entityList.splice(0, entityList.length);

}