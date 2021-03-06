"use strict";
/**
 * Drawing canvas
 *
 * @author Guangcong Luo <guangcongluo@gmail.com>
 * @license MIT
 */
function h(tagName, attrs) {
    var children = [];
    for (var _i = 2; _i < arguments.length; _i++) {
        children[_i - 2] = arguments[_i];
    }
    var elem = typeof tagName === 'string' ? document.createElement(tagName) : tagName;
    if (attrs) {
        var style = attrs.style;
        if (attrs.class)
            elem.className = attrs.class;
        delete attrs.style;
        delete attrs.class;
        Object.assign(elem, attrs);
        if (style)
            Object.assign(elem.style, style);
    }
    for (var _a = 0, children_1 = children; _a < children_1.length; _a++) {
        var child = children_1[_a];
        elem.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
    }
    return elem;
}
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
        this.clickColor = function (ev) {
            var value = ev.currentTarget.value;
            _this.strokeColor = value;
            _this.updateButtons();
        };
        this.clickStrokeWidth = function (ev) {
            var value = ev.currentTarget.value;
            _this.strokeWidth = parseInt(value);
            _this.updateButtons();
        };
        this.undo = function () {
            if (_this.empty())
                return;
            _this.strokes.pop();
            _this.redraw();
            _this.updateButtons();
        };
        this.clear = function () {
            if (_this.empty())
                return;
            _this.strokes = [];
            _this.redraw();
            _this.updateButtons();
        };
        this.empty = function() {
            return _this.strokes.length == 0;
        }
        this.mousedown = function (ev) {
            if (ev.type == "mousedown" && ev.button != 0) {
                return;
            }
            ev.preventDefault();
            var _a = _this.getPosition(ev), x = _a[0], y = _a[1];
            _this.currentStroke = {
                points: [[x, y]],
                color: _this.strokeColor,
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
            if (ev.type == "mouseup" && ev.button != 0) {
                return;
            }
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
            h("div", { class: "top-controls", style: { marginBottom: '4px' } },
                h("button", { name: "undo", onclick: this.undo }, "Undo"),
                " ",
                h("button", { name: "clear", onclick: this.clear }, "Clear")),
            h("div", { class: "left-controls", style: { marginBottom: '4px' } },
                h("button", { onclick: this.clickColor, value: "black", title: "black" },
                    h("span", { class: "color", style: { background: 'black', display: 'inline-block', width: '12px', height: '12px' } })),
                " ",
                h("button", { onclick: this.clickColor, value: "#F55252", title: "red" },
                    h("span", { class: "color", style: { background: '#F55252', display: 'inline-block', width: '12px', height: '12px' } })),
                " ",
                h("button", { onclick: this.clickColor, value: "#F8BC01", title: "yellow" },
                    h("span", { class: "color", style: { background: '#F8BC01', display: 'inline-block', width: '12px', height: '12px' } })),
                " ",
                h("button", { onclick: this.clickColor, value: "#3DC853", title: "green" },
                    h("span", { class: "color", style: { background: '#3DC853', display: 'inline-block', width: '12px', height: '12px' } })),
                " ",
                h("button", { onclick: this.clickColor, value: "#42B0FF", title: "blue" },
                    h("span", { class: "color", style: { background: '#42B0FF', display: 'inline-block', width: '12px', height: '12px' } })),
                " ",
                h("button", { onclick: this.clickColor, value: "#D512F9", title: "purple" },
                    h("span", { class: "color", style: { background: '#D512F9', display: 'inline-block', width: '12px', height: '12px' } })),
                " ",
                h("button", { onclick: this.clickColor, value: "#8D6E63", title: "brown" },
                    h("span", { class: "color", style: { background: '#8D6E63', display: 'inline-block', width: '12px', height: '12px' } })),
                " ",
                "| ",
                h("button", { onclick: this.clickStrokeWidth, value: "1" }, "Thin"),
                " ",
                h("button", { onclick: this.clickStrokeWidth, value: "2" }, "Normal"),
                " ",
                h("button", { onclick: this.clickStrokeWidth, value: "4" }, "Thick")),
            h("div", { style: { width: styleWidth, height: styleHeight, border: "1px solid gray", boxSizing: "content-box" } },
                this.drawingCanvas = h("canvas", { width: this.w, height: this.h,
                    style: { width: styleWidth, height: styleHeight, display: 'block', position: 'absolute' } }),
                this.currentStrokeCanvas = h("canvas", { width: this.w, height: this.h,
                    style: { width: styleWidth, height: styleHeight, display: 'block', position: 'absolute' } }),
                this.interfaceCanvas = h("canvas", { width: this.w, height: this.h,
                    style: { width: styleWidth, height: styleHeight, display: 'block', position: 'absolute',
                             cursor: 'crosshair' },
                    onmousedown: this.mousedown, onmousemove: this.mousemove, onmouseup: this.mouseup,
                    onmouseout: this.mouseup, ontouchstart: this.mousedown, ontouchmove: this.mousemove,
                    ontouchend: this.mouseup, ontouchcancel: this.mouseup }))));
        window.addEventListener("beforeunload", function( event ) {
          if (!_this.empty()) {
            event.preventDefault();
          }
        });
        this.wrapper = wrapper;
        this.interfaceContext = this.interfaceCanvas.getContext('2d');
        this.currentStrokeContext = this.currentStrokeCanvas.getContext('2d');
        this.drawingContext = this.drawingCanvas.getContext('2d');
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
            this.drawStroke(this.drawingContext, stroke);
        }
    };
    CanvasDraw.prototype.drawStroke = function (context, stroke) {
        var _a;
        context.strokeStyle = stroke.color;
        context.lineWidth = stroke.width * 2 * this.pixelRatio;
        context.lineCap = 'round';
        context.lineJoin = 'round';
        var _b = stroke.points[0], x = _b[0], y = _b[1];
        context.beginPath();
        context.moveTo(x, y);
        for (var i = 1; i < stroke.points.length; i++) {
            _a = stroke.points[i], x = _a[0], y = _a[1];
            context.lineTo(x, y);
        }
        context.stroke();
    };
    CanvasDraw.prototype.commitStroke = function () {
        if (!this.currentStroke)
            return;
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
            if (button.name === 'undo' || button.name === 'clear') {
                button.disabled = !this.strokes.length;
            }
            else {
                button.disabled = (button.value === this.strokeColor || button.value === "" + this.strokeWidth);
            }
        }
    };
    return CanvasDraw;
}());
//# sourceMappingURL=canvas-draw.js.map