import fs from "fs";
import { createCanvas } from "canvas";
import { createContext } from "./utils.js";

function generate(folder, name, _canvas) {
  fs.writeFileSync(`./${folder}/${name}.png`, _canvas.toBuffer("image/png"));
}

let i = 0;

const drawNewCanvas = (number) => {
  const n = 255 - number;
  const canvas = createCanvas(48, 48);

  const { canvas: newCanvas } = createContext(canvas, n);

  generate("images", n, newCanvas);
};

const drawCanvases = (start = 0, finish = 256) => {
  let _i = start;

  while (_i < finish) {
    drawNewCanvas(_i);
    _i++;
  }

  i++;
};

drawCanvases(0, 2000);
