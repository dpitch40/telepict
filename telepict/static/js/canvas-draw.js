"use strict";
/**
 * Drawing canvas
 *
 * @author Guangcong Luo <guangcongluo@gmail.com>
 * @license MIT
 */
var colorSelector = document.getElementById('color-picker');
var clear = new Object();

var CanvasDraw = /** @class */ (function () {
    function CanvasDraw(wrapper) {
        var _this = this;
        this.strokes = [];
        this.currentStroke = null;
        this.pixelRatio = window.devicePixelRatio || 1;
        this.w = 320 * this.pixelRatio;
        this.h = 320 * this.pixelRatio;
        this.strokeWidth = 2;
        this.strokeColor = 'black';
        this.erase = false;
        colorSelector.onchange = function () {
            _this.strokeColor = this.dataset.currentColor;
            _this.erase = false;
            _this.updateButtons();
        };
        this.clickEraser = function (ev) {
            _this.erase = !_this.erase;
            _this.updateButtons();
        };
        this.widthAdjust = function (ev) {
            var value = ev.target.value;
            _this.widthLabel.innerHTML = "Width: " + value;
            _this.strokeWidth = parseFloat(value);
        };
        this.undo = function () {
            if (!_this.strokes.length)
                return;
            _this.strokes.pop();
            _this.redraw();
            _this.updateButtons();
        };
        this.clear = function () {
            if (!_this.strokes.length)
                return;
            _this.strokes.push(clear);
            _this.redraw();
            _this.updateButtons();
        };
        this.reset = function () {
            _this.strokes = [];
            _this.redraw();
            _this.updateButtons();
        };
        this.empty = function() {
            return _this.strokes.length == 0;
        };
        this.mousedown = function (ev) {
            ev.preventDefault();
            var _a = _this.getPosition(ev), x = _a[0], y = _a[1];
            _this.currentStroke = {
                points: [[x, y]],
                color: _this.strokeColor,
                erase: _this.erase,
                width: _this.strokeWidth,
            };
            _this.draw(x, y);
        };
        this.mousemove = function (ev) {
            var _a = _this.getPosition(ev), x = _a[0], y = _a[1];
            if (_this.currentStroke) {
                _this.currentStroke.points.push([x, y]);
            }
            _this.draw(x, y);
        };
        this.mouseup = function (ev) {
            if (_this.currentStroke) {
                var _a = _this.getPosition(ev), x = _a[0], y = _a[1];
                _this.currentStroke.points.push([x, y]);
                _this.commitStroke();
                _this.draw(x, y);
            }
        };
        if (wrapper && wrapper.dataset.dimensions) {
            var _a = wrapper.dataset.dimensions.split('x'), width = _a[0], height = _a[1];
            this.w = Math.round(parseInt(width) * this.pixelRatio);
            this.h = Math.round(parseInt(height) * this.pixelRatio);
        }
        if (!wrapper)
            wrapper = document.createElement('div');
        wrapper.innerHTML = '';
        var styleWidth = Math.round(this.w / this.pixelRatio) + "px";
        var styleHeight = Math.round(this.h / this.pixelRatio) + "px";
        wrapper.appendChild(h("div", null,
            h("div", { class: "left-controls", style: { marginBottom: '4px' } },
                h("button", { class: "btn btn-primary", onclick: this.clickEraser, title: "eraser" }, "Erase"),
                "  ",
                h("label", { id: "width-input-label", for: "width-input", class: "form-label",
                            style: {width: "6em"}}, "Width: 3"),
                h("input", { id: "width-input", type: "range", min: "0.5", max: "15", value: "3",
                            step: "0.5", class: "form-range w-25", oninput: this.widthAdjust}),
                "  ",
                h("button", { class: "btn btn-primary", name: "undo", onclick: this.undo }, "Undo"),
                "  ",
                h("button", { class: "btn btn-primary", name: "clear", onclick: this.clear }, "Clear")),
            h("div", { style: { width: styleWidth, height: styleHeight, border: "1px solid gray", boxSizing: "content-box" } },
                this.drawingCanvas = h("canvas", { width: this.w, height: this.h, style: { width: styleWidth, height: styleHeight, display: 'block', position: 'absolute' } }),
                this.currentStrokeCanvas = h("canvas", { width: this.w, height: this.h, style: { width: styleWidth, height: styleHeight, display: 'block', position: 'absolute' } }),
                this.interfaceCanvas = h("canvas", { width: this.w, height: this.h, style: { width: styleWidth, height: styleHeight, display: 'block', position: 'absolute', cursor: 'crosshair' }, onmousedown: this.mousedown, onmousemove: this.mousemove, onmouseup: this.mouseup, onmouseout: this.mouseup, ontouchstart: this.mousedown, ontouchmove: this.mousemove, ontouchend: this.mouseup, ontouchcancel: this.mouseup }))));
        this.wrapper = wrapper;
        this.interfaceContext = this.interfaceCanvas.getContext('2d');
        this.currentStrokeContext = this.currentStrokeCanvas.getContext('2d');
        this.drawingContext = this.drawingCanvas.getContext('2d');
        this.widthLabel = document.getElementById('width-input-label');
        this.updateButtons();
        this.redraw();
    }
    CanvasDraw.prototype.getPosition = function (ev) {
        var rect = this.interfaceCanvas.getBoundingClientRect();
        var x = ev.clientX;
        var y = ev.clientY;
        // use first touch if available
        var touches = ev.changedTouches;
        if (touches && touches.length > 0) {
            x = touches[0].clientX;
            y = touches[0].clientY;
        }
        // It's impossible to get the actual coordinates on a Retina screen, so we have to approximate
        return [(x - rect.left) * this.pixelRatio, (y - rect.top) * this.pixelRatio];
    };
    CanvasDraw.prototype.draw = function (x, y) {
        // draw cursor
        this.interfaceContext.clearRect(0, 0, this.w, this.h);
        this.interfaceContext.lineWidth = this.pixelRatio;
        this.interfaceContext.strokeStyle = 'gray';
        this.interfaceContext.beginPath();
        this.interfaceContext.arc(x, y, this.strokeWidth * this.pixelRatio, 0, Math.PI * 2);
        this.interfaceContext.stroke();
        // current stroke
        this.currentStrokeContext.clearRect(0, 0, this.w, this.h);
        if (!this.currentStroke)
            return;
        this.drawStroke(this.currentStrokeContext, this.currentStroke);
    };
    CanvasDraw.prototype.redraw = function () {
        this.drawingContext.fillStyle = 'white';
        this.drawingContext.fillRect(0, 0, this.w, this.h);
        for (var _i = 0, _a = this.strokes; _i < _a.length; _i++) {
            var stroke = _a[_i];
            if (stroke.erase === true) {
                this.drawingContext.globalCompositeOperation = 'destination-out';
            }
            else {
                this.drawingContext.globalCompositeOperation = 'source-over';
            }
            this.drawStroke(this.drawingContext, stroke);
        }
    };
    CanvasDraw.prototype.drawStroke = function (context, stroke) {
        if (stroke === clear) {
            context.clearRect(0, 0, this.w, this.h);
        } else {
            if (stroke.erase === true) {
                context.strokeStyle = "white";
            }
            else {
                context.strokeStyle = stroke.color;
            }
            context.lineWidth = stroke.width * 2 * this.pixelRatio;
            context.lineCap = 'round';
            context.lineJoin = 'round';
            var _a = stroke.points[0], x = _a[0], y = _a[1];
            var _b;
            context.beginPath();
            context.moveTo(x, y);
            for (var i = 1; i < stroke.points.length; i++) {
                _b = stroke.points[i], x = _b[0], y = _b[1];
                context.lineTo(x, y);
            }
            context.stroke();
        }
    };
    CanvasDraw.prototype.commitStroke = function () {
        if (!this.currentStroke)
            return;
        if (this.currentStroke.erase === true) {
            this.drawingContext.globalCompositeOperation = 'destination-out';
        }
        else {
            this.drawingContext.globalCompositeOperation = 'source-over';
        }
        this.strokes.push(this.currentStroke);
        this.currentStroke = null;
        this.drawingContext.drawImage(this.currentStrokeCanvas, 0, 0, this.w, this.h);
        this.currentStrokeContext.clearRect(0, 0, this.w, this.h);
        this.updateButtons();
    };
    CanvasDraw.prototype.updateButtons = function () {
        var buttons = this.wrapper.getElementsByTagName('button');
        for (var _i = 0, buttons_1 = buttons; _i < buttons_1.length; _i++) {
            var button = buttons_1[_i];
            var disable;
            if (button.title == "eraser") {
                if (this.erase) {
                    button.classList.add('active');
                } else {
                    button.classList.remove('active');
                }
            } else {
                if (button.name === 'undo') {
                    disable = !this.strokes.length;
                } else if (button.name === 'clear') {
                    disable = !this.strokes.length || this.strokes[this.strokes.length - 1] === clear;
                }
                if (disable) {
                    button.disabled = true;
                }
                else {
                    button.disabled = false;
                }
            }
        }
    };
    return CanvasDraw;
}());
