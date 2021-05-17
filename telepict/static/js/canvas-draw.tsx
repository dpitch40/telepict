/**
 * Drawing canvas
 *
 * @author Guangcong Luo <guangcongluo@gmail.com>
 * @license MIT
 */

interface Stroke {
  color: string;
  width: number;
  points: [number, number][],
}

function h<T extends HTMLElement = HTMLElement>(
  tagName: string | T, attrs?: any, ...children: (HTMLElement | string)[]
): T {
  const elem = typeof tagName === 'string' ? document.createElement(tagName) as T : tagName;
  if (attrs) {
    const style = attrs.style;
    if (attrs.class) elem.className = attrs.class;
    delete attrs.style;
    delete attrs.class;
    Object.assign(elem, attrs);
    if (style) Object.assign(elem.style, style);
  }
  for (const child of children) {
    elem.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
  }
  return elem;
}
declare namespace JSX {
  type Element = any;
  interface IntrinsicElements { [k: string]: any; }
}

class CanvasDraw {
  wrapper: HTMLDivElement;

  /** mostly just holds the cursor */
  interfaceCanvas: HTMLCanvasElement;
  currentStrokeCanvas: HTMLCanvasElement;
  drawingCanvas: HTMLCanvasElement;

  interfaceContext: CanvasRenderingContext2D;
  currentStrokeContext: CanvasRenderingContext2D;
  drawingContext: CanvasRenderingContext2D;

  strokes: Stroke[] = [];
  currentStroke: Stroke | null = null;

  pixelRatio = window.devicePixelRatio || 1;
  w = 320 * this.pixelRatio;
  h = 320 * this.pixelRatio;

  strokeWidth = 2;
  strokeColor = 'black';

  constructor(wrapper?: HTMLDivElement | null) {
    if (wrapper && wrapper.dataset.dimensions) {
      const [width, height] = wrapper.dataset.dimensions.split('x');
      this.w = Math.round(parseInt(width) * this.pixelRatio);
      this.h = Math.round(parseInt(height) * this.pixelRatio);
    }
    if (!wrapper) wrapper = document.createElement('div');
    wrapper.innerHTML = '';

    const styleWidth = `${Math.round(this.w / this.pixelRatio)}px`;
    const styleHeight = `${Math.round(this.h / this.pixelRatio)}px`;

    wrapper.appendChild(<div>
      <div class="top-controls" style={{marginBottom: '4px'}}>
        <button class="btn btn-primary" name="undo" onclick={this.undo}>Undo</button> {}
        <button class="btn btn-primary" name="clear" onclick={this.clear}>Clear</button>
      </div>
      <div class="left-controls" style={{marginBottom: '4px'}}>
        <button class="btn btn-primary" onclick={this.clickColor} value="black" title="black">
          <span class="color" style={{background: 'black', display: 'inline-block', width: '12px', height: '12px'}}></span>
        </button> {}
        <button class="btn btn-primary" onclick={this.clickColor} value="#F55252" title="red">
          <span class="color" style={{background: '#F55252', display: 'inline-block', width: '12px', height: '12px'}}></span>
        </button> {}
        <button class="btn btn-primary" onclick={this.clickColor} value="#F8BC01" title="yellow">
          <span class="color" style={{background: '#F8BC01', display: 'inline-block', width: '12px', height: '12px'}}></span>
        </button> {}
        <button class="btn btn-primary" onclick={this.clickColor} value="#3DC853" title="green">
          <span class="color" style={{background: '#3DC853', display: 'inline-block', width: '12px', height: '12px'}}></span>
        </button> {}
        <button class="btn btn-primary" onclick={this.clickColor} value="#42B0FF" title="blue">
          <span class="color" style={{background: '#42B0FF', display: 'inline-block', width: '12px', height: '12px'}}></span>
        </button> {}
        <button class="btn btn-primary" onclick={this.clickColor} value="#D512F9" title="purple">
          <span class="color" style={{background: '#D512F9', display: 'inline-block', width: '12px', height: '12px'}}></span>
        </button> {}
        <button class="btn btn-primary" onclick={this.clickColor} value="#8D6E63" title="brown">
          <span class="color" style={{background: '#8D6E63', display: 'inline-block', width: '12px', height: '12px'}}></span>
        </button> | {}
        <button class="btn btn-primary" onclick={this.clickEraser} title="eraser">
          Erase
        </button> {}
        | {}
        <button class="btn btn-primary" onclick={this.clickStrokeWidth} value="1">
          Thin
        </button> {}
        <button class="btn btn-primary" onclick={this.clickStrokeWidth} value="2">
          Normal
        </button> {}
        <button class="btn btn-primary" onclick={this.clickStrokeWidth} value="4">
          Thick
        </button>
      </div>
      <div style={{width: styleWidth, height: styleHeight, border: `1px solid gray`, boxSizing: `content-box`}}>
        {this.drawingCanvas = <canvas
          width={this.w} height={this.h}
          style={{width: styleWidth, height: styleHeight, display: 'block', position: 'absolute'}}
        ></canvas>}

        {this.currentStrokeCanvas = <canvas
          width={this.w} height={this.h}
          style={{width: styleWidth, height: styleHeight, display: 'block', position: 'absolute'}}
        ></canvas>}
    
        {this.interfaceCanvas = <canvas
          width={this.w} height={this.h}
          style={{width: styleWidth, height: styleHeight, display: 'block', position: 'absolute', cursor: 'crosshair'}}
          onmousedown={this.mousedown}
          onmousemove={this.mousemove}
          onmouseup={this.mouseup}
          onmouseout={this.mouseup}
          ontouchstart={this.mousedown}
          ontouchmove={this.mousemove}
          ontouchend={this.mouseup}
          ontouchcancel={this.mouseup}
        ></canvas>}
      </div>
    </div>);

    this.wrapper = wrapper;
    this.interfaceContext = this.interfaceCanvas.getContext('2d')!;
    this.currentStrokeContext = this.currentStrokeCanvas.getContext('2d')!;
    this.drawingContext = this.drawingCanvas.getContext('2d')!;

    this.updateButtons();
    this.redraw();
  }

  getPosition(ev: MouseEvent | TouchEvent): [number, number] {
    const rect = this.interfaceCanvas.getBoundingClientRect();

    let x = (ev as MouseEvent).clientX;
    let y = (ev as MouseEvent).clientY;

    // use first touch if available
    const touches = (ev as TouchEvent).changedTouches;
    if (touches && touches.length > 0) {
      x = touches[0].clientX;
      y = touches[0].clientY;
    }

    // It's impossible to get the actual coordinates on a Retina screen, so we have to approximate
    return [(x - rect.left) * this.pixelRatio, (y - rect.top) * this.pixelRatio];
  }

  draw(x: number, y: number) {
    // draw cursor
    this.interfaceContext.clearRect(0, 0, this.w, this.h);
    this.interfaceContext.lineWidth = this.pixelRatio;
    this.interfaceContext.strokeStyle = 'gray';
    this.interfaceContext.beginPath();
    this.interfaceContext.arc(x, y, this.strokeWidth * this.pixelRatio, 0, Math.PI * 2);
    this.interfaceContext.stroke();

    // current stroke
    this.currentStrokeContext.clearRect(0, 0, this.w, this.h);

    if (!this.currentStroke) return;
    this.drawStroke(this.currentStrokeContext, this.currentStroke);
  }
  redraw() {
    this.drawingContext.fillStyle = 'white';
    this.drawingContext.fillRect(0, 0, this.w, this.h);
    for (const stroke of this.strokes) {
      if (stroke.color == "") {
          this.drawingContext.globalCompositeOperation = 'destination-out';
      } else {
          this.drawingContext.globalCompositeOperation = 'source-over';
      }
      this.drawStroke(this.drawingContext, stroke);
    }
  }
  drawStroke(context: CanvasRenderingContext2D, stroke: Stroke) {
    if (stroke.color == "") {
        context.strokeStyle = "white";
    } else {
        context.strokeStyle = stroke.color;
    }
    context.lineWidth = stroke.width * 2 * this.pixelRatio;
    context.lineCap = 'round';
    context.lineJoin = 'round';

    let [x, y] = stroke.points[0];
    context.beginPath();
    context.moveTo(x, y);
    for (let i = 1; i < stroke.points.length; i++) {
      [x, y] = stroke.points[i];
      context.lineTo(x, y);
    }
    context.stroke();
  }
  commitStroke() {
    if (!this.currentStroke) return;
    if (this.currentStroke.color == "") {
        this.drawingContext.globalCompositeOperation = 'destination-out';
    } else {
        this.drawingContext.globalCompositeOperation = 'source-over';
    }
    this.strokes.push(this.currentStroke);
    this.currentStroke = null;
    this.drawingContext.drawImage(this.currentStrokeCanvas, 0, 0, this.w, this.h);
    this.currentStrokeContext.clearRect(0, 0, this.w, this.h);
    this.updateButtons();
  }

  updateButtons() {
    const buttons = this.wrapper.getElementsByTagName('button') as any as HTMLButtonElement[];
    for (const button of buttons) {
      var active;
      if (button.name === 'undo' || button.name === 'clear') {
        active = !this.strokes.length;
      } else {
        active = (button.value === this.strokeColor || button.value === `${this.strokeWidth}` ||
                          (button.title == "eraser" && this.strokeColor == ""));
      }
      if (active) {
          button.classList.add("active");
      } else {
          button.classList.remove("active");
      }
    }
  }
  clickColor = (ev: Event) => {
    const value = (ev.currentTarget as HTMLButtonElement).value;
    this.strokeColor = value;
    this.updateButtons();
  };
  clickEraser = (ev: Event) => {
    this.strokeColor = "";
    this.updateButtons();
  };
  clickStrokeWidth = (ev: Event) => {
    const value = (ev.currentTarget as HTMLButtonElement).value;
    this.strokeWidth = parseInt(value);
    this.updateButtons();
  };
  undo = () => {
    if (!this.strokes.length) return;
    this.strokes.pop();
    this.redraw();
    this.updateButtons();
  }
  clear = () => {
    if (!this.strokes.length) return;
    this.strokes = [];
    this.redraw();
    this.updateButtons();
  }
  mousedown = (ev: MouseEvent | TouchEvent) => {
    ev.preventDefault();
    const [x, y] = this.getPosition(ev);
    this.currentStroke = {
      points: [[x, y]],
      color: this.strokeColor,
      width: this.strokeWidth,
    };
    this.draw(x, y);
  };
  mousemove = (ev: MouseEvent | TouchEvent) => {
    const [x, y] = this.getPosition(ev);
    if (this.currentStroke) {
      this.currentStroke.points.push([x, y]);
    }
    this.draw(x, y);
  };
  mouseup = (ev: MouseEvent | TouchEvent) => {
    if (this.currentStroke) {
      const [x, y] = this.getPosition(ev);
      this.currentStroke.points.push([x, y]);
      this.commitStroke();
      this.draw(x, y);
    }
  };
}
