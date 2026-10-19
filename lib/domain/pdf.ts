import fontData from "./dejavu-font.json" with { type: "json" };
import type { DeliverySnapshot } from "./model.ts";
import { renderText } from "./exports.ts";
// Embedded DejaVu Sans subset, matching Style Guide v1.1. Text-only internal simulation layout.
export function renderPdf(s:DeliverySnapshot):Buffer {
 const lines=renderText(s).replace(/[—–]/g,"-").split("\n").flatMap(line=>{
  const words=line.split(/\s+/),rows:string[]=[];let current="";
  for(const word of words){
   for(let start=0;start<word.length||start===0;start+=85){
    const part=word.slice(start,start+85);
    if((current+" "+part).length>85){rows.push(current);current=part;}else current+=(current?" ":"")+part;
   }
  }rows.push(current);return rows;
 });
 const pages:string[][]=[];for(let i=0;i<lines.length;i+=47)pages.push(lines.slice(i,i+47));
 const objects:Buffer[]=[];
 const add=(s:string)=>objects.push(Buffer.from(s,"latin1"));
 add('<< /Type /Catalog /Pages 2 0 R >>');
 add(`<< /Type /Pages /Kids [${pages.map((_,i)=>`${4+i*2} 0 R`).join(" ")}] /Count ${pages.length} >>`);
 const descriptor=4+pages.length*2,fontFile=descriptor+1;
 add(`<< /Type /Font /Subtype /TrueType /BaseFont /DejaVuSans /Encoding /WinAnsiEncoding /FirstChar 32 /LastChar 255 /Widths [${fontData.widths.join(' ')}] /FontDescriptor ${descriptor} 0 R >>`);
 pages.forEach((page,i)=>{
  add(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents ${5+i*2} 0 R >>`);
  const escape=(s:string)=>s.replace(/[^\x20-\xff]/g,"?").replace(/([\\()])/g,"\\$1");
  const stream=`BT /F1 10 Tf 0.04 0.15 0.23 rg 48 792 Td 15 TL\n${page.map(line=>`(${escape(line)}) Tj T*`).join("\n")}\nET`;
  add(`<< /Length ${Buffer.byteLength(stream,"latin1")} >>\nstream\n${stream}\nendstream`);
 });
 add(`<< /Type /FontDescriptor /FontName /DejaVuSans /Flags 32 /FontBBox [-1021 -463 1793 1232] /ItalicAngle 0 /Ascent 928 /Descent -236 /CapHeight 729 /StemV 80 /FontFile2 ${fontFile} 0 R >>`);
 const font=Buffer.from(fontData.font,"base64");objects.push(Buffer.concat([Buffer.from(`<< /Length ${font.length} /Length1 ${font.length} >>\nstream\n`),font,Buffer.from('\nendstream')]));
 let offset=0;const chunks:Buffer[]=[];const push=(b:Buffer)=>{chunks.push(b);offset+=b.length;};
 push(Buffer.from('%PDF-1.4\n%\xe2\xe3\xcf\xd3\n','latin1'));const offsets=[0];
 objects.forEach((obj,i)=>{offsets.push(offset);push(Buffer.from(`${i+1} 0 obj\n`));push(obj);push(Buffer.from('\nendobj\n'));});
 const xref=offset;push(Buffer.from(`xref\n0 ${objects.length+1}\n0000000000 65535 f \n${offsets.slice(1).map(n=>`${String(n).padStart(10,"0")} 00000 n \n`).join("")}trailer\n<< /Size ${objects.length+1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`));
 return Buffer.concat(chunks);
}
