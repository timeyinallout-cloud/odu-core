// The bijection in JavaScript. Run: node examples/01_bytes_and_figures.mjs
import { fromByte, toByte, encode, decode } from "odu-core";

for (const b of [0, 44, 255]) {
  console.log(String(b).padStart(3), "->", fromByte(b).name);
}

if (toByte(fromByte(200)) !== 200) throw new Error("byte round-trip failed");

const message = Buffer.from("Ẹ káàbọ̀", "utf-8");
const back = Buffer.from(decode(encode(message)));
if (!back.equals(message)) throw new Error("data round-trip failed");
console.log(`\nround-trip of ${message.length} bytes: OK`);
