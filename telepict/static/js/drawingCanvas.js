var canvasDraw = new CanvasDraw(document.getElementById('image-canvas'));

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

function passDrawing() {
  if (!canvasDraw.empty()) {
    canvasDraw.drawingCanvas.toBlob(function (blob) {
      var url = httpHost + '/img_upload';

      var formData = new FormData();
      formData.set('file', blob, 'drawing.png');
      formData.set('game_id', game_id);
      formData.set('player_id', player_id);

      var request = new XMLHttpRequest();
      request.open('POST', url, true);
      request.send(formData);
      updateDisplaySent('drawing');
      request.onload = function(event) {
        ws.send(JSON.stringify({'action': 'update'}));
      }
    });
  }
}

if (!HTMLCanvasElement.prototype.toBlob) {
  // polyfill toBlob
  HTMLCanvasElement.prototype.toBlob = function(callback, type, quality) {
    var canvas = this;
    setTimeout(function () {
      var binStr = atob(canvas.toDataURL(type, quality).split(',')[1]);
      var len = binStr.length;
      var arr = new Uint8Array(len);

      for (var i = 0; i < len; i++) {
        arr[i] = binStr.charCodeAt(i);
      }

      callback(new Blob([arr], {type: type || 'image/png'}));
    });
  };
}
