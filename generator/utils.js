export const randomIntFromInterval = (min, max) => {
  return Math.floor(Math.random() * (max - min + 1) + min);
};

export const strRandom = (length) => {
  let result = "";
  const characters = "abcdefghijklmnopqrstuvwxyz0123456789";

  // Loop to generate characters for the specified length
  for (let i = 0; i < length; i++) {
    const randomInd = Math.floor(Math.random() * characters.length);
    result += characters.charAt(randomInd);
  }
  return result;
};

export const luminance = ({ r, g, b }) => {
  const r1 = r / 255;
  const g1 = g / 255;
  const b1 = b / 255;

  return 0.2126 * r1 + 0.7152 * g1 + 0.0722 * b1;
};

export const getRatio = (color1, color2) => {
  const L1 = Math.max(luminance(color1), luminance(color2));
  const L2 = Math.min(luminance(color1), luminance(color2));

  const contrast = (L1 + 0.05) / (L2 + 0.05);

  return contrast;
};

export const createContext = (canvas, n) => {
  const context = canvas.getContext("2d");

  const textR = randomIntFromInterval(n - randomIntFromInterval(0, 255), n);
  const textG = randomIntFromInterval(n - randomIntFromInterval(0, 255), n);
  const textB = randomIntFromInterval(n - randomIntFromInterval(0, 255), n);

  const backgroundR = randomIntFromInterval(0, 255);
  const backgroundG = randomIntFromInterval(0, 255);
  const backgroundB = randomIntFromInterval(0, 255);

  const fontNumber = randomIntFromInterval(8, 48);

  context.fillStyle = `rgb(${backgroundR}, ${backgroundG}, ${backgroundB})`;
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.font = `${fontNumber}px ${
    fontNumber % randomIntFromInterval(0, 5) == 0 ? "serif" : "sans-serif"
  }`;
  context.textAlign = "center";
  context.fillStyle = "rgb(" + textR + "," + textG + "," + textB + ")";

  context.fillText(strRandom(randomIntFromInterval(1, 10)), 15, 30);

  return {
    canvas,
    contrastRatio: getRatio(
      { r: textR, g: textG, b: textB },
      { r: backgroundR, g: backgroundG, b: backgroundB }
    ),
  };
};
