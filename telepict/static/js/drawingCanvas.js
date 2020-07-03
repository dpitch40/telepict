var imageInput = document.querySelector('#image-canvas');

// Color selection
var colorSelect = document.querySelector('#color-select');

var selectedColor;
var selectableColors = [];
for (const option of colorSelect.querySelectorAll('option')) {
  selectableColors.push(option.value);
}
function colorSelected(event) {
  selectedColor = colorSelect.selectedIndex;
}
colorSelect.addEventListener('input', colorSelected);
colorSelected();

// Size selection
var sizeSelect = document.querySelector('#size-select');
var selectedSize;
function sizeSelected(event) {
  selectedSize = Number(sizeSelect.value);
}
sizeSelect.addEventListener('input', sizeSelected);
sizeSelected();

// Set up drawing canvas
var drawingContext = imageInput.getContext("2d");
var clickX = new Array();
var clickY = new Array();
var clickColors = new Array();
var clickSizes = new Array();
var clickDrag = new Array();
var inBounds = false;
var mouseDown = false;

imageInput.onmousedown = function(event) {
  var mouseX = event.pageX - this.offsetLeft;
  var mouseY = event.pageY - this.offsetTop;

  mouseDown = true;
  addClick(event.pageX - this.offsetLeft, event.pageY - this.offsetTop, false);
  redraw();
}
imageInput.onmousemove = function(event) {
  if (inBounds && mouseDown){
    addClick(event.pageX - this.offsetLeft, event.pageY - this.offsetTop, true);
    redraw();
  }
}
document.querySelector('body').onmouseup = function(event) {
  mouseDown = false;
}
imageInput.onmouseenter = function(event) {
  inBounds = true;
  if (mouseDown) {
    addClick(event.pageX - this.offsetLeft, event.pageY - this.offsetTop, false);
    redraw();
  }
}
imageInput.onmouseleave = function(event) {
  inBounds = false;
}
var clickX = new Array();

function addClick(x, y, dragging) {
  clickX.push(x);
  clickY.push(y);
  clickColors.push(selectedColor);
  clickSizes.push(selectedSize);
  clickDrag.push(dragging);
}
function redraw() {
  drawingContext.clearRect(0, 0, drawingContext.canvas.width,
                           drawingContext.canvas.height); // Clears the canvas

  drawingContext.lineJoin = "round";

  for(var i=0; i < clickX.length; i++) {
    drawingContext.strokeStyle = selectableColors[clickColors[i]];
    drawingContext.lineWidth = clickSizes[i];
    drawingContext.beginPath();
    if(clickDrag[i] && i){
      drawingContext.moveTo(clickX[i-1], clickY[i-1]);
     } else{
       drawingContext.moveTo(clickX[i]-1, clickY[i]);
     }
     drawingContext.lineTo(clickX[i], clickY[i]);
     drawingContext.closePath();
     drawingContext.stroke();
  }
}
function clearCanvas() {
  clickX = new Array();
  clickY = new Array();
  clickDrag = new Array();
  redraw();
}

function compressImageData(imgData) {
  const compressedData = new Array();
  const data = imgData.data;
  var x;
  var y;
  for (let i = 0; i < data.length; i += 4) {
    if (data[i+3] > 0) {
      x = (i % (imgData.width * 4) / 4);
      y = Math.floor(i / (imgData.width * 4));
      compressedData.push(x, y, data[i], data[i+1], data[i+2], data[i+3]);
    }
  }
  return Uint16Array.from(compressedData);
}

function sendImage() {
  var files = imgUpload.files;
  var file, request, formData;
  if (files.length > 0) {
    file = files[0];

    formData = new FormData();
    formData.set('file', file, file.name);
    formData.set('game_id', game_id);
    formData.set('player_id', player_id);

    url = httpHost + '/img_upload'
    request = new XMLHttpRequest();
    request.open('POST', url, true);
    request.send(formData);
    request.onload = function(event) {
      ws.send('UPDATE:');
    }
  }
}
