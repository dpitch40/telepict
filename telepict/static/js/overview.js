const overviewCanvas = document.querySelector('#overview-canvas');
const overviewCtx = overviewCanvas.getContext('2d');

overviewCanvas.style = 'background-color: #eeeeee';
const fontHeight = 30;
const overviewFont = fontHeight + 'px sans-serif';
const stackFontHeight = 20;
const stackFont = stackFontHeight + 'px sans-serif';

const arrowAngleOffset = 0.25;
const arrowHeadAngle = Math.PI / 3;
const arrowHeadLength = 15;

var overviewWidth;
var overviewHeight;
var circleCenterX;
var circleCenterY;
var circleRadiusX;
var circleRadiusY;

const colors = ['black', 'red', 'green', 'blue', 'orange', 'teal', 'darkviolet',
                'salmon', 'seagreen', 'slateblue', 'grey', 'maroon', 'olive', 'navy'];

function indexColor(i) {
  return colors[i % colors.length];
}

function clearOverview() {
  overviewCtx.clearRect(0, 0, overviewWidth, overviewHeight);
}

function determineOverviewSize(overview) {
  overviewWidth = 450 + 50 * overview.circle.length;
  overviewHeight = 100 + 50 * overview.circle.length;
  circleCenterX = overviewWidth / 2;
  circleCenterY = overviewHeight / 2;
  circleRadiusX = circleCenterX * 0.75;
  circleRadiusY = circleCenterY * 0.75;
  overviewCanvas.width = overviewWidth;
  overviewCanvas.height = overviewHeight;
}

function drawArrowHeads(startAngle, endAngle) {
  const endX = circleCenterX + circleRadiusX * Math.cos(endAngle);
  const endY = circleCenterY + circleRadiusY * Math.sin(endAngle);

  const tangentRise = Math.cos(endAngle);
  const tangentRun = Math.sin(endAngle) * circleRadiusX / circleRadiusY;
  var tangentAngle = Math.atan2(tangentRise, tangentRun) + Math.PI;
  // Have to reverse the angle again, since Math.atan2 measures counterclockwise from the positive
  // X-axis which is the reverse of our coordinate system
  if (endAngle < startAngle) {
    tangentAngle += Math.PI;
  }

  const headAngle1 = tangentAngle + Math.PI - arrowHeadAngle / 2;
  const hx1 = endX + Math.cos(headAngle1) * arrowHeadLength;
  const hy1 = endY - Math.sin(headAngle1) * arrowHeadLength;
  overviewCtx.beginPath();
  overviewCtx.moveTo(endX, endY);
  overviewCtx.lineTo(hx1, hy1);
  overviewCtx.stroke();

  const headAngle2 = tangentAngle + Math.PI + arrowHeadAngle / 2;
  const hx2 = endX + Math.cos(headAngle2) * arrowHeadLength;
  const hy2 = endY - Math.sin(headAngle2) * arrowHeadLength;
  overviewCtx.beginPath();
  overviewCtx.moveTo(endX, endY);
  overviewCtx.lineTo(hx2, hy2);
  overviewCtx.stroke();
}

function drawArrows(overview) {
  const circle = overview.circle
  var startAngle, endAngle;
  const stepSize = 2 * Math.PI / circle.length;
  overviewCtx.strokeStyle = 'black';
  overviewCtx.lineWidth = 3;
  for (let i = 0; i < circle.length; i++) {
    if (overview.clockwise) {
      startAngle = 5 * Math.PI / 2 - (i + arrowAngleOffset) * stepSize;
      endAngle = 5 * Math.PI / 2 - (i + 1 - arrowAngleOffset) * stepSize;
    } else {
      startAngle = Math.PI / 2 + (i + arrowAngleOffset) * stepSize;
      endAngle = Math.PI / 2 + (i + 1 - arrowAngleOffset) * stepSize;
    }

    overviewCtx.beginPath();
    overviewCtx.ellipse(circleCenterX, circleCenterY, circleRadiusX, circleRadiusY,
                        0, startAngle, endAngle, overview.clockwise);
    overviewCtx.stroke();

    // Becuase the coordinate system is flipped vertically, the "startAngle" of the arc
    // is actually the one we want to draw the arrow heads on
    drawArrowHeads(endAngle, startAngle);
  }
}

function drawStackIndicator(x, y, width, number, color) {
  overviewCtx.fillStyle = color;
  overviewCtx.strokeStyle = color;
  overviewCtx.lineWidth = 3;
  overviewCtx.fillText(' ' + number, x, y - (fontHeight - stackFontHeight) * 0.6);
  overviewCtx.beginPath();
  overviewCtx.moveTo(x + width * 0.2, y);
  overviewCtx.lineTo(x + width, y);
  overviewCtx.stroke();
}

function drawNames(overview) {
  const circle = overview.circle
  var player, angle, x, y, text, textWidth, origWidth, indicatorWidth;
  var indicatorWidths;
  for (let i = 0; i < circle.length; i++) {
    indicatorWidths = [];
    player = circle[i];

    angle = Math.PI * (-1 / 2 - 2 * i / circle.length);

    overviewCtx.font = overviewFont;
    text = overviewCtx.measureText(player[0]);
    textWidth = text.width;
    origWidth = textWidth;

    // Add width of stack indicators
    overviewCtx.font = stackFont;
    for (const stack of player[1]) {
      indicatorWidth = overviewCtx.measureText(' ' + stack[0]).width;
      indicatorWidths.push(indicatorWidth);
      textWidth += indicatorWidth;
    }

    x = circleCenterX + Math.cos(angle) * circleRadiusX - textWidth / 2;
    y = circleCenterY - Math.sin(angle) * circleRadiusY + fontHeight / 2;

    overviewCtx.font = overviewFont;
    overviewCtx.fillStyle = indexColor(i);
    overviewCtx.fillText(player[0], x, y);

    x += origWidth;
    overviewCtx.font = stackFont;
    for (let j = 0; j < player[1].length; j++) {
      drawStackIndicator(x, y, indicatorWidths[j], player[1][j][0], indexColor(player[1][j][2]));
      x += indicatorWidths[j];
    }
  }
}

function drawNumRounds(numRounds) {
  if (numRounds > 1) {
    const s = 'x ' + numRounds;
    overviewCtx.font = overviewFont;
    text = overviewCtx.measureText(s);
    x = circleCenterX - text.width / 2;
    y = circleCenterY + fontHeight / 2;
    overviewCtx.fillStyle = 'black';
    overviewCtx.fillText(s, x, y);
  }
}

function renderOverview(overview) {
  clearOverview();
  determineOverviewSize(overview);
  drawArrows(overview);
  drawNames(overview);
  drawNumRounds(overview.num_rounds);
}
