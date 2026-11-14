// 16 Proof Frame: an ad frame around a result. A customer comment as the hook, a huge silver headline,
// a tilted BEFORE phone behind a big AFTER phone joined by a dotted arrow, and a price pill.
// The plan's clips are the AFTER (big phone, with their sound); "before" plays silently in the small one.
import { existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { missing } from "./scripts/fonts.mjs";

export const NAME = "proof-frame";
export const TALKS = false;
export const FIT = [600, 1066]; // the AFTER phone's screen
export const EXTRA = (plan) => [{ name: "before", clip: plan.before, fit: [404, 718], hold: true }];

const SKILL_DIR = dirname(fileURLToPath(import.meta.url));
const ROLES = ["comment", "headline", "sub", "price"];
const FONTS = { headline: "Oswald[wght].ttf", other: "Inter[opsz,wght].ttf" };

export function validate(plan) {
  const b = plan.before;
  if (!b || typeof b !== "object" || !String(b.src ?? "").trim())
    throw new Error('the plan needs "before": {"src": "raw/before.mp4"}, the clip or photo for the tilted phone');
  const seen = new Set();
  for (const t of plan.texts ?? []) {
    if (!ROLES.includes(t.role))
      throw new Error(`text role "${t.role}" is not used by this look. Use ${ROLES.map((r) => `"${r}"`).join(", ")}.`);
    if (seen.has(t.role)) throw new Error(`only one "${t.role}" text: the frame stays the same for the whole video`);
    seen.add(t.role);
    if (!String(t.text ?? "").trim()) throw new Error(`the "${t.role}" text is empty`);
    if (t.role === "comment" && !String(t.name ?? "").trim())
      throw new Error('the "comment" needs a "name": the small grey line above it, e.g. "хэрэглэгч"');
    if (t.start !== undefined && !(Number(t.start) >= 0)) throw new Error(`"${t.text}": "start" must be a number of seconds`);
    const font = FONTS[t.role] ?? FONTS.other;
    for (const s of t.role === "comment" ? [t.text, t.name] : [t.text]) {
      const bad = missing(String(s), join(SKILL_DIR, "fonts", font));
      if (bad.length) throw new Error(`"${s}" uses ${bad.join(" ")}, which ${font.split("[")[0]} can't draw`);
    }
  }
  const accent = plan.look?.accent;
  if (accent !== undefined && !/^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(String(accent)))
    throw new Error('"accent" must be a colour like "#E8663A"');
}

const text = (plan, role) => (plan.texts ?? []).find((t) => t.role === role);

// When the price pops: its own start, else 3 s before the end (not before the entrance settles),
// and never later than 1.5 s before the end, so it can be read.
export function priceAt(price, dur) {
  const at = price.start !== undefined ? Number(price.start) : Math.max(1.2, dur - 3);
  return Math.max(0, Math.min(at, dur - 1.5));
}

export async function prepare(ctx) {
  if (!existsSync(join(ctx.work, "media", "before.mp4")))
    throw new Error('the BEFORE video is missing. Run "prep plan.json" again.');
  const price = text(ctx.plan, "price");
  return { priceAt: price ? priceAt(price, ctx.dur) : null };
}

// Soft on purpose (Saagii, 14 Nov: "tone down"); members raise them with "sfx": {"volume": …}.
export function sfx(plan, ctx) {
  const out = [];
  if (text(plan, "comment")) out.push({ sound: "notify", at: 0, volume: 0.4 });
  out.push({ sound: "whoosh", at: 0.2, volume: 0.3 });
  const price = text(plan, "price");
  if (price) out.push({ sound: "ding", at: Math.round((priceAt(price, ctx.dur) + 0.15) * 1000) / 1000, volume: 0.5 });
  return out;
}
