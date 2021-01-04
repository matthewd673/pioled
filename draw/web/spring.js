var canvas;
var context;
var canvasBounding;
var resourcesReady;

var entityList = [];
var renderList = [];

var mouseX = 0;
var mouseY = 0;
var mouseDown = false;
var leftMouseDown = false;
var middleMouseDown = false;
var rightMouseDown = false;

//SETUP
window.onload = function() {
    onStart();
}

function onStart() { }

function createCanvas(width, height, container = "")
{
    var newCanvas = document.createElement("canvas");
    newCanvas.setAttribute("id", "spring-surface");
    newCanvas.setAttribute("width", width.toString());
    newCanvas.setAttribute("height", height.toString());

    newCanvas.oncontextmenu = function(event) {
        event.preventDefault();
    }
    
    canvas = newCanvas;

    if (container != "")
        document.getElementById(container).appendChild(canvas);
    else
        document.body.appendChild(canvas);
    
    context = canvas.getContext("2d");
    canvasBounding = canvas.getBoundingClientRect();
    setupInput();
}

function setCanvas(canvasId)
{
    canvas = document.getElementById(canvasId);
    context = canvas.getContext("2d");
    canvasBounding = canvas.getBoundingClientRect();
    setupInput();
}
//END SETUP

//RENDERING CLASSES
class Sprite
{
    
    constructor(imageSource, x, y, width, height,)
    {
        this.render = true;
        this.ready = false;
        
        var image = new Image();
        image.onload = function() { this.ready = true; };
        image.src = imageSource;
        
        this.image = image;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;

        entityList.push(this);
    }
    
}

class Rectangle
{
    constructor(x, y, width, height, color = "black", filled = true)
    {
        this.render = true;

        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.color = color;
        this.filled = filled;

        entityList.push(this);
    }
}

class Circle
{
    constructor(x, y, radius, color = "black", filled = true)
    {
        this.render = render;
        
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.color = color;
        this.filled = filled;

        entityList.push(this);
    }
}

class Line
{
    constructor(startPoint, endPoint, color)
    {
        this.render = true;
        
        this.startPoint = startPoint;
        this.endPoint = endPoint;
        this.color = color;

        entityList.push(this);
    }
}

class Point
{
    constructor(x, y)
    {
        this.x = x;
        this.y = y;
    }
}

class Text
{
    constructor(text, x = 0, y = 0, font = "12px serif", color = "black", filled = true)
    {
        this.render = true;
        
        this.text = text;
        this.x = x;
        this.y = y;
        this.font = font;
        this.color = color;
        this.filled = filled;

        entityList.push(this);
    }
}
//END RENDERING CLASSES

//RENDERING HELPERS
function hide(renderObject)
{
    renderObject.render = false;
}

function show(renderObject)
{
    renderObject.render = true;
}

function toggle(renderObject)
{
    renderObject.render = !renderObject.render;
}
//END RENDERING HELPERS

//INPUT SETUP
function setupInput()
{
    canvas.addEventListener("click", canvasClicked);
    canvas.addEventListener("mousemove", canvasMouseMoved);
    canvas.addEventListener("mousedown", canvasMouseDown);
    canvas.addEventListener("mouseup", canvasMouseUp);

    window.addEventListener("keydown", windowKeyDown);
    window.addEventListener("keyup", windowKeyUp);
    window.addEventListener("keypress", windowKeyPress);
}
//END INPUT SETUP

//INPUT STUFF
function canvasClicked(event)
{
    onClick(getMouseButton(event.button));
}
function onClick(button) { }

function canvasMouseMoved(event)
{
    mouseX = event.clientX - canvasBounding.left;
    mouseY = event.clientY - canvasBounding.top;
    onMouseMove(mouseX, mouseY);
}
function onMouseMove(x, y) { }

function canvasMouseDown(event)
{
    mouseDown = true;
    if (event.button == 0)
        leftMouseDown = true;
    if (event.button == 1)
        middleMouseDown = true;
    if (event.button == 2)
        rightMouseDown = true;
    
    onMouseDown(getMouseButton(event.button));
}
function onMouseDown(button) { }

function canvasMouseUp(event)
{
    mouseDown = false;
    if (event.button == 0)
        leftMouseDown = false;
    if (event.button == 1)
        middleMouseDown = false;
    if (event.button == 2)
        rightMouseDown = false;
    
    onMouseUp(getMouseButton(event.button));
}
function onMouseUp(button) { }

function windowKeyDown(event)
{
    onKeyDown(new Key(event.keyCode, String.fromCharCode(event.keyCode)));
}
function onKeyDown(key) { }

function windowKeyUp(event)
{
    onKeyUp(new Key(event.keyCode, String.fromCharCode(event.keyCode)));
}
function onKeyUp(key) { }

function windowKeyPress(event)
{
    onKeyPress(new Key(event.keyCode, String.fromCharCode(event.keyCode)));
}
function onKeyPress(key) { }

function getMouseButton(button)
{
    if (button == 0)
        return "left";
    if (button == 1)
        return "middle";
    if (button == 2)
        return "right;"
}

//END INPUT

//INPUT CLASSES

class Key
{
    constructor(code, char)
    {
        this.code = code;
        this.char = char;
    }
}
//END INPUT CLASSES

//UPDATE FUNCTIONS
function update()
{
    onUpdate();
    //check each resource to see if it's ready
    if(!resourcesReady)
    {
        var readyCount = 0;
        for(var i = 0; i < renderList.length; i++)
        {
            if(renderList[i].ready)
                readyCount++;
        }
        if(readyCount == renderList.length - 1)
            resourcesReady = true;
    }
    render();
}

function onUpdate() {} //just here to prevent errors

function render()
{
    onRender();

    context.clearRect(0, 0, canvas.width, canvas.height);
    for(var i = 0; i < renderList.length; i++)
    {
        var current = renderList[i];
        var type = current.constructor.name;
        
        if(current.render && inFrame(current))
        {
            if(type == "Sprite")
                context.drawImage(current.image, current.x, current.y, current.width, current.height);
            if(type == "Rectangle")
            {
                if(current.filled)
                {
                    context.fillStyle = current.color;
                    context.fillRect(current.x, current.y, current.width, current.height);
                }
                else
                {
                    context.strokeStyle = current.color;
                    context.strokeRect(current.x, current.y, current.width, current.height);
                }
            }
            if(type == "Circle")
            {
                if(current.filled)
                    context.fillStyle = current.color;
                else
                    context.strokeStyle = current.color;
                    
                context.beginPath();
                context.arc(current.x + current.radius, current.y + current.radius, current.radius, 0, 2 * Math.PI);
                if(current.filled)
                {
                    context.closePath();
                    context.fill();
                }
                else
                    context.stroke();
                
            }
            if(type == "Line")
            {
                context.strokeStyle = current.color;
                
                context.beginPath();
                context.moveTo(current.startPoint.x, current.startPoint.y);
                context.lineTo(current.endPoint.x, current.endPoint.y);
                context.stroke();
            }
            if(type == "Text")
            {
                if(current.filled)
                    context.fillStyle = current.color;
                else
                    context.strokeStyle = current.color;
                    
                context.font = current.font;
                
                if(current.filled)
                    context.fillText(current.text, current.x, current.y);
                else
                    context.strokeText(current.text, current.x, current.y);
            }
        }
    }
    
    renderList.splice(0, renderList.length);
    
}

function onRender() { drawAll(); } //draw all by default

//END UPDATE FUNCTIONS

function draw(renderObject)
{
    renderList.push(renderObject);
}

function drawAll()
{
    entityList.forEach(renderObject => renderList.push(renderObject));
}

function inFrame(renderObject)
{
    var type = renderObject.constructor.name;
    var specialCheck = false;
    
    if(type == "Line")
        specialCheck = true;

    if(!specialCheck && renderObject.x > canvasBounding.width || renderObject.y > canvasBounding.height || (renderObject.x + renderObject.width) < 0 || (renderObject.y + renderObject.height) < 0) //incomplete
        return false;
    else
        return true;
    
}

function play(fps = 60)
{
    window.setInterval(update, 1000 / fps);
}

//UTILITIES
function getPNG()
{
    canvas.toDataURL("image/png");
}

function randInt(min = 0, max = 1)
{
    return Math.round(Math.random() * (max - min) + min);
}

function hideCursor()
{
    canvas.style.cursor = "none";
}

function showCursor()
{
    canvas.style.cursor = "normal";
}

function outlineCanvas()
{
    canvas.style.border = "1px solid black";
}