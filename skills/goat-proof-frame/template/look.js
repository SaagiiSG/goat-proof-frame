// 16 Proof Frame. Reads window.PLAN (written by goat.mjs) and builds one paused GSAP timeline.
// Frame 0 is the thumbnail: everything is already there at 92% size and 60% opacity, then settles.
const P = window.PLAN;
const $ = (s) => document.querySelector(s);
const text = (role) => P.texts.find((t) => t.role === role);
const tl = gsap.timeline({ paused: true });
const FROM = { opacity: 0.6, scale: 0.92 };
const IN = { opacity: 1, scale: 1, x: 0, y: 0, duration: 0.6, ease: "power3.out" };

const root = $("#root");
if (P.look.accent) root.style.setProperty("--accent", P.look.accent);

// Top stack: comment (the hook), silver headline, sub pill. Missing roles are just left out.
const cm = text("comment"), hl = text("headline"), sp = text("sub"), pp = text("price");
if (cm) {
  $("#cm small").textContent = cm.name;
  $("#cm b").textContent = cm.text;
  tl.fromTo("#cm", { ...FROM, y: -24 }, { ...IN }, 0);
} else $("#cm").remove();

const lines = hl ? hl.text.split("\n") : [];
for (const l of lines) $("#hl").appendChild(document.createElement("div")).textContent = l;
if (hl) {
  $("#hl div").appendChild(document.createElement("i")); // sits on the baseline, so layout() can find the letters
  tl.fromTo("#hl", { ...FROM }, { ...IN, duration: 0.65 }, 0.08);
} else $("#hl").remove();

if (sp) {
  $("#sp .t").textContent = sp.text;
  tl.fromTo("#sp", { ...FROM, y: 16 }, { ...IN }, 0.16);
} else $("#sp").remove();

// Phones: BEFORE slides in from the left, AFTER rises; the whole stage then creeps 2.5% closer.
// The phone bodies stay solid (a see-through phone shows the horizon through it); their screens light up from 60%.
$("#bf .tag").textContent = P.look.before_label ?? "ӨМНӨ";
$("#af .tag").textContent = P.look.after_label ?? "ДАРАА";
gsap.set("#bf", { rotation: -9 });
tl.fromTo("#bf", { scale: 0.92, x: -36 }, { ...IN, duration: 0.7 }, 0.1);
tl.fromTo("#af", { scale: 0.92, y: 70 }, { ...IN, duration: 0.7 }, 0.2);
tl.fromTo(".scr", { opacity: 0.6 }, { opacity: 1, duration: 0.7, ease: "power2.out", stagger: 0.1 }, 0.1);
gsap.set("#stage", { transformOrigin: "540px 640px" }); // the arrow's peak stays put, clear of the sub pill
tl.fromTo("#stage", { scale: 1 }, { scale: 1.025, duration: P.dur, ease: "none" }, 0);

// Dotted arrow from the BEFORE's top to the AFTER's top, drawing itself, then its head.
// It lands just right of the AFTER's tag, so layout() redraws it once the tag's real width is known.
const pen = $("#pen");
pen.setAttribute("pathLength", "1"); // the draw tween runs 1 -> 0 whatever the curve's length
pen.setAttribute("stroke-dasharray", "1 1");
function arrow(endX) {
  const S = [300, 742], C1 = [360, 610], C2 = [endX - 96, 590], E = [endX, 726];
  const d = `M${S} C${C1} ${C2} ${E}`;
  $("#dots").setAttribute("d", d);
  pen.setAttribute("d", d);
  const ang = Math.atan2(E[1] - C2[1], E[0] - C2[0]) + Math.PI;
  const wing = (a) => `${E[0] + 26 * Math.cos(ang + a)},${E[1] + 26 * Math.sin(ang + a)}`;
  $("#head").setAttribute("d", `M${wing(-0.55)} L${E} L${wing(0.55)}`);
}
arrow(636);
tl.fromTo(pen, { attr: { "stroke-dashoffset": 1 } }, { attr: { "stroke-dashoffset": 0 }, duration: 0.6, ease: "power2.inOut" }, 0.75);
tl.fromTo("#head", { opacity: 0 }, { opacity: 1, duration: 0.15 }, 1.3);

// Price: pops in at its time (or settles like the rest if it is there from the start).
if (pp) {
  $("#pp .t").textContent = pp.text;
  if (P.priceAt < 0.3) tl.fromTo("#pp", { ...FROM }, { ...IN }, 0);
  else {
    tl.fromTo("#pp", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1.08, duration: 0.2, ease: "power2.out" }, P.priceAt);
    tl.to("#pp", { scale: 1, duration: 0.15, ease: "power1.inOut" }, P.priceAt + 0.2);
  }
} else $("#pp").remove();

tl.set({}, {}, P.dur);
window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;

// Sizes need the real fonts; the renderer waits for document.fonts.ready before the first frame.
const canvas = document.createElement("canvas").getContext("2d");
function layout() {
  if (cm) {
    GOAT.fit($("#cm b"), 710, 40, 24);
    GOAT.fit($("#cm small"), 710, 24, 18);
  }
  if (sp) GOAT.fit($("#sp .t"), 680, 34, 22);
  if (pp) GOAT.fit($("#pp .t"), 302, 40, 24); // the pill ends by x 520: over the BEFORE, off the AFTER's result
  const tag = $("#af .tag"); // AFTER phone left 410 + bezel 20
  arrow(Math.max(636, 430 + tag.offsetLeft + tag.offsetWidth + 50));
  if (!hl) return;
  // headline: fits 840 px wide and at most 130 px of ink, centred between the comment and the sub pill
  const e = $("#hl");
  let size = GOAT.fit(e, 840, 170, 56);
  const ink = () => {
    canvas.font = `700 ${size}px Oswald`;
    const first = canvas.measureText(lines[0]), last = canvas.measureText(lines.at(-1));
    const pitch = lines.length > 1 ? e.children[1].offsetTop - e.children[0].offsetTop : 0;
    return { asc: first.actualBoundingBoxAscent, h: (lines.length - 1) * pitch + first.actualBoundingBoxAscent + last.actualBoundingBoxDescent };
  };
  let m = ink();
  if (m.h > 130) {
    e.style.fontSize = `${(size = (size * 130) / m.h)}px`;
    m = ink();
  }
  const top = cm ? $("#cm").offsetTop + $("#cm").offsetHeight : 270, bottom = sp ? $("#sp").offsetTop : 640;
  const base = e.querySelector("i").offsetTop; // the first line's baseline, from the top of #hl
  e.style.top = `${(top + bottom) / 2 - m.h / 2 - (base - m.asc)}px`;
}
layout();
document.fonts.ready.then(layout);
