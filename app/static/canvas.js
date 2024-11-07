import { createContext } from "./utils.js";

let i = 0;
let ratio = 4.5;
const root = document.getElementById("canvases");

const drawNewCanvas = (number) => {
  const n = 255 - (number % 255);
  const canvas = document.createElement("canvas");

  canvas.height = 48;
  canvas.width = 48;
  canvas.style.float = "left";
  canvas.style.margin = "10px";

  const { canvas: newCanvas, contrastRatio } = createContext(canvas, n);

  newCanvas.style.outline =
    contrastRatio >= ratio ? "2px solid lightGreen" : "";

  root.append(newCanvas);
};

const drawCanvases = (start = 0, finish = 256) => {
  let _i = start;

  while (_i < finish) {
    drawNewCanvas(_i);
    _i++;
  }

  i++;
};

const setupSelect = () => {
  const select = document.getElementById("ratio");

  select.style.display = "block";
  select.style.margin = "10px";

  select.addEventListener("change", () => {
    ratio = parseInt(select.value, 10);
    root.innerHTML = "";
    drawCanvases();
  });
};

setupSelect();
drawCanvases(0, 200);
