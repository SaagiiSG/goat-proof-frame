---
name: goat-proof-frame
description: Proof Frame · Нотолгоо хүрээ. Wraps a finished video in an ad frame that proves the result. A customer comment pill as the hook, a huge silver condensed headline, a tilted BEFORE phone (the raw clip or photo) behind a bigger AFTER phone (the finished video, with its sound), joined by a dotted arc arrow, and a price pill that pops at the end, on a charcoal backdrop with a glowing horizon. Renders a 1080x1920 MP4 for Reels/TikTok. Best for hair, nails, beauty, barbers, auto detailing and ecommerce showing a transformation, and for showing off an edit (raw footage vs the finished reel). Use whenever the user wants a before-and-after ad, a "өмнө / дараа" video, to prove a result, or to show raw footage next to the finished edit, or types /goat-proof-frame, /нотолгоо, or says "өмнө дараа видео хий", "үр дүнгээ харуулъя", "make a before and after ad", even if they don't name the skill.
---

# Proof Frame · Нотолгоо хүрээ

An ad frame around a result. At the top, a white comment pill quotes a doubt ("Үнэхээр ийм болох уу?"). Under it, a huge silver headline answers it, then a small pill says what was done. In the middle, a tilted BEFORE phone sits behind a bigger AFTER phone, joined by a dotted arc arrow; both play at once. Near the end a white price pill pops in. It is the only GOAT look that puts one finished video inside another to prove a result.

**Good for:** hair colour and cuts, nails, makeup, barbers, car detailing, cleaning, furniture and room makeovers, product edits; also raw footage vs a finished reel (to sell editing or a GOAT skill).
**Not for:** talking-head advice (try Grid Explainer), results that need more than 10–15 s to see, and weight, skin or body results in paid ads (see Rules).

Talk to the user in the language they write in (usually Mongolian). Keep messages short and plain; many users are not technical. `SKILL_DIR` means this skill's base directory (shown when the skill loads). Run commands from the user's project folder with absolute paths into `SKILL_DIR`.

## 1. Setup check (first time on a machine)

Run `ffmpeg -version` and `uv --version`. If either is missing, show the install command and ask before installing (it is their computer):
- Mac: `brew install ffmpeg uv`
- Windows: `winget install Gyan.FFmpeg` and `winget install astral-sh.uv`, then close and reopen the terminal.

The first render downloads a small Python package (Pillow) once. After that it is instant.

## 2. Collect the clips and words

Make `raw/` and `output/` in the current folder. Ask for:
1. **The AFTER video:** the finished result. A finished reel, or a clip of the done work (the new haircut turning to camera, the clean car). Its sound plays. 8–15 s is best: the frame stays the same the whole time, so longer gets dull.
2. **The BEFORE:** one clip or one photo of how it was. Film it from the same angle as the AFTER if you can. If the clip is shorter than the AFTER, its last frame holds.
3. **The words:**
   - a comment: a doubt real customers say, 3–6 words ("Үнэхээр ийм болох уу?"). Use a real comment or a question they hear often. Never invent a customer's name.
   - a headline: 1–3 words in capitals that answer it ("ЖИНХЭНЭ ҮР ДҮН", "2 ЦАГТ").
   - a sub line: what was done ("Үс засалт + будаг").
   - a price line: the offer ("Үнэ 45 000₮"). Never invent a price. Ask.

If this folder was already edited with another GOAT skill, its `output/*.mp4` is a good AFTER and the raw clip a good BEFORE.

Then run: `uv run SKILL_DIR/scripts/goatcut.py probe raw/*`
It prints each file's size, length, whether it has sound and whether it is HDR.

## 3. Write plan.json

Write `plan.json` in the project folder. Paths are relative to it.

```json
{
  "output": "output/proof-frame.mp4",
  "clips": [{"src": "output/hair-reel.mp4", "in": 0.0, "out": 10.0}],
  "before": {"src": "raw/IMG_0410.MOV", "in": 2.0},
  "texts": [
    {"role": "comment", "text": "Үнэхээр ийм болох уу?", "name": "хэрэглэгч · 2м"},
    {"role": "headline", "text": "ЖИНХЭНЭ ҮР ДҮН"},
    {"role": "sub", "text": "Үс засалт + будаг"},
    {"role": "price", "text": "Үнэ 45 000₮", "start": 6.5}
  ],
  "look": {"accent": "#E8663A", "before_label": "ӨМНӨ", "after_label": "ДАРАА"}
}
```

**clips** are the AFTER video. They play in the big phone, in order, with their sound; the video is as long as they are. `in`/`out` trim (seconds). `cx`/`cy` (0–1, default 0.5) choose which part of a wide clip the phone keeps.
**before** is one clip or photo for the tilted phone. `in`/`out` trim a clip, `cx`/`cy` as above. It plays silently, starting at the same moment as the AFTER; when it runs out, its last frame holds. A photo holds the whole time.

How the two play together: the render reads the AFTER clips as its main video and opens a second ffmpeg reader for the BEFORE, so both phones move at once from one plan.

**texts** (each shows from `start` to `end`, default the whole video; only one of each role at a time):
- `comment`: the hook pill at the top. `name` is the small grey line above it, default "хэрэглэгч".
- `headline`: the huge silver capitals. Long words shrink to fit; "\n" makes two lines, but one line reads bigger.
- `sub`: the small pill under the headline, with a coloured dot and an arrow button.
- `price`: the white price pill over the phones. Give it a `start` 2–4 s before the end; it pops in then.

The comment, headline and sub land one after another in the first second, the BEFORE phone slides in at 0.5 s, the AFTER rises at 0.7 s and the arrow draws at 1 s. Start the AFTER on something worth seeing about 1 s in.

**Auto sound effects:** a notification as the comment pill appears, a whoosh as the phones fly in, a ding as the price pill lands. If the AFTER is a finished reel with its own music, skip extra music.
**look** options:
- `accent`: colour of the dots and the arrow button. Default `#E8663A` (warm orange). Use the brand colour if the user has one.
- `before_label` / `after_label`: the small tags on the phones. Default `ӨМНӨ` / `ДАРАА`. For an edit, "ТҮҮХИЙ" / "ЭДИТ" also work.

Before rendering, tell the user the plan in plain words (which clip is before, which is after, the four lines) and ask "OK?". This is the only approval needed.

<!-- audio: this section is copied from core/skill-audio.md by build.py; edit it there -->
## Sound effects, voice-over and music

**Sound effects are on by default.** The look adds its own (see "Auto sound effects" above). They are made in code, so there's nothing to license, and they sit quietly under the voice.
- Turn them off: `"sfx": false`. Make them quieter or louder: `"sfx": {"volume": 0.6}`.
- Add one: `"sfx": {"add": [{"sound": "ding", "at": 4.2}]}`. Sounds: whoosh, swish, pop, click, type, shutter, boom, thud, hit, riser, ding, notify, shimmer, paper, tape, marker, projector, tick. `type`, `marker`, `projector` and `riser` also take `"dur"` in seconds; a riser should end on the moment it builds to.
- Let the user hear one render before adding more. Too many sounds feel cheap.

**Voice-over.** If the user wants to talk over the video, ask them to record it on their phone (a voice memo is fine: m4a, mp3 or wav) and copy it into `raw/`. Then add `"voiceover": {"src": "raw/vo.m4a", "at": 0.5}` (`at` = when it starts; optional `"volume"`). While the voice plays, the clips' own sound and the music dip automatically. Run `goatcut.py probe raw/vo.m4a` to get its `speech` spans and time the words on screen to them. The clips must add up to at least the voice-over's length (the render warns if not). Recording tips for the user: a small quiet room (a parked car or a wardrobe works), phone about 20 cm from the mouth, read the script out loud once before recording.

**Music.** `"music": {"src": "raw/song.mp3", "volume": 0.25}`. Only use music the user has the rights to. Music added inside the Instagram/TikTok app is the safe choice, so suggest that first.
<!-- /audio -->

## 4. Render and check

`uv run SKILL_DIR/scripts/render.py plan.json`

A 10 s video takes about 10 s. Then look at two frames before saying it is done:
`ffmpeg -y -loglevel error -ss 3 -i output/proof-frame.mp4 -frames:v 1 output/check-1.jpg` and the same with `-ss` 1 s before the end. Read them. Check that the headline is not cut off, the result is clear in the AFTER phone (fix with `cx`/`cy` or `in`), and the price pill does not hide the important part of the BEFORE.

If a render fails twice, stop and explain the error in plain words. Don't loop.

## 5. Hand over

Tell the user where the file is (`output/proof-frame.mp4`) and that it is ready to post.

## Rules

- **Paid ads:** if the user will run this as a paid ad about weight, skin or the body (weight loss, acne, wrinkles, cellulite, body shape), warn them first: Meta restricts before-and-after images for health and cosmetic claims, and the ad may be rejected. Hair, nails, cars and rooms are fine.
- Show the BEFORE as it really was. Don't darken, blur or pick a worse clip on purpose.
- The price sits inside the area no app buttons cover. Put the price, phone or offer only in `price`, never in the comment.
- Use only the fonts bundled in `SKILL_DIR/fonts` (Oswald and Inter; they have Ө ө Ү ү). Don't swap in other fonts.
- The output is 1080x1920, 30 fps, H.264, sound normalised to -14 LUFS (Instagram/TikTok level).
