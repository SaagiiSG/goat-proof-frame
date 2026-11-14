---
name: goat-proof-frame
description: Proof Frame · Нотолгоо хүрээ. Wraps the member's own result in an ad frame that proves it. A customer comment pill as the hook, a huge silver condensed headline, a tilted BEFORE phone (a clip or photo of how it was) behind a big AFTER phone (a clip of the finished result itself, with its sound), joined by a dotted arrow that draws itself, and a price pill that pops near the end, on a charcoal backdrop with a glowing horizon. Built on HyperFrames. Renders a 1080x1920 MP4 for Reels/TikTok. Best for hair, nails, beauty, barbers, auto detailing, cleaning and room makeovers showing a transformation. Use whenever the user wants a before-and-after ad, a "өмнө / дараа" video, to prove a result, or types /goat-proof-frame, /нотолгоо, or says "өмнө дараа видео хий", "үр дүнгээ харуулъя", "make a before and after ad", even if they don't name the skill.
---

# Proof Frame · Нотолгоо хүрээ

An ad frame around a result. At the top, a white comment pill quotes a doubt ("Үнэхээр ийм болох уу?"). Under it, a huge silver headline answers it, then a small pill says what was done. Below, a tilted BEFORE phone sits behind a big AFTER phone that fills the lower half of the screen, and a dotted arrow draws itself from one to the other; both play at once. Near the end a white price pill pops in. The whole frame is already there on the first frame (it is the Reels thumbnail), then settles into place. It is the only GOAT look that puts the result inside a phone to prove it.

**Good for:** hair colour and cuts, nails, makeup, barbers, car detailing, cleaning, furniture and room makeovers, product repairs.
**Not for:** talking-head advice (try Grid Explainer), results that need more than 10–15 s to see, and weight, skin or body results in paid ads (see Rules). If the user has no BEFORE (no clip or photo of how it was), say so and suggest another GOAT look.

Talk to the user in the language they write in (usually Mongolian). Keep messages short and plain; many users are not technical. `SKILL_DIR` means this skill's base directory (shown when the skill loads). Run commands from the user's project folder with absolute paths into `SKILL_DIR`. `goat` below means `node SKILL_DIR/scripts/goat.mjs`.

## 1. Setup check (first time on a machine)

Run `node --version` (needs 22 or newer) and `ffmpeg -version`. If either is missing, show the install command and ask before installing (it is their computer):
- Mac: `brew install node ffmpeg`
- Windows: `winget install OpenJS.NodeJS.LTS` and `winget install Gyan.FFmpeg`, then close and reopen the terminal.

This look has no captions, so it needs no speech model. The first render downloads, once, a private copy of Chrome that draws the frames. Tell the user the first run takes a while; after that it starts at once. Nothing is uploaded: everything runs on their computer, with no account.

**Long steps:** the first `render` (the Chrome download) can run longer than a normal command timeout. Run it in the background, or with a 600000 ms timeout, and wait for it to end. Never stop it and start it again.

**Windows has not been tested yet.** If a step fails there, show the error to the user in plain words.

## 2. Collect the clips

Make `raw/` and `output/` in the current folder. Ask for:
1. **The AFTER:** a clip of the finished result itself, filmed on their phone: the new haircut turning to the camera, the finished nails under the lamp, the clean car, the room after. Its sound plays. 6–15 s is best: the frame stays the same the whole time, so longer gets dull. **Never use an edited reel or another GOAT video as the AFTER**: the frame is the edit, and the viewer must see the real result.
2. **The BEFORE:** one clip or one photo of how it was. Film it from the same angle as the AFTER if you can. If the clip is shorter than the AFTER, its last frame holds. A photo holds the whole time.
3. **The words:**
   - a comment: a doubt real customers say, 3–6 words ("Үнэхээр ийм болох уу?"), and the small grey line above it (`name`). Use a real comment or a question they hear often. Never invent a customer's name or a time: if it isn't a real comment the user can show, the name is just "хэрэглэгч". A time ("· 2м") goes in only when it comes from that real comment.
   - a headline: 1–3 words in capitals that answer it ("ЖИНХЭНЭ ҮР ДҮН", "2 ЦАГТ").
   - a sub line: what was done ("Үс засалт + будаг").
   - a price line: the offer ("Үнэ 45 000₮"). Never invent a price. Ask.

**What to film** (tell the user before they shoot, if they haven't yet): phone upright, the result in the middle of the screen and well lit, the same spot and angle for before and after. The AFTER phone keeps the whole upright frame; the BEFORE phone keeps most of it.

Then run `goat probe raw/*`. It prints each file's size, length, whether it has sound, and whether it is HDR.

## 3. Prepare

Write `plan.json` in the project folder (paths are relative to it):

```json
{
  "output": "output/proof-frame.mp4",
  "clips": [{"src": "raw/IMG_0415.MOV", "in": 1.0, "out": 11.0}],
  "before": {"src": "raw/IMG_0410.JPG"},
  "texts": [
    {"role": "comment", "name": "хэрэглэгч · 2м", "text": "Үнэхээр ийм болох уу?"},
    {"role": "headline", "text": "ЖИНХЭНЭ ҮР ДҮН"},
    {"role": "sub", "text": "Үс засалт + будаг"},
    {"role": "price", "text": "Үнэ 45 000₮", "start": 7.0}
  ],
  "look": {"accent": "#E8663A"}
}
```

**clips** are the AFTER. They play in the big phone, in order, with their sound; the video is as long as they are. `in`/`out` trim a video (seconds). Add `"sound": false` to mute one clip. `cx`/`cy` (0–1, default 0.5) choose which part of a wider frame the phone keeps.
**before** is one clip or photo for the tilted phone. `in`/`out` trim a clip, `cx`/`cy` as above. It plays silently, starting with the AFTER.

Then run these in order. Each one says what to run first if a step is missing.
1. `goat prep plan.json`: fits the AFTER to the big phone's screen and the BEFORE to the small one, and writes both into `.work-proof-frame/`. **Run it again whenever `clips` or `before` change.**
2. `goat cut plan.json`: this look never cuts pauses; the step only readies the video for `render` and takes a second.

## 4. Write the words

**texts** (one of each at most; each stays on the whole video):
- `comment`: the hook pill at the top. `name` (required) is the small grey line above it.
- `headline`: the huge silver capitals. Long words shrink to fit; "\n" makes two lines, but one line reads bigger.
- `sub`: the small pill under the headline, with a coloured dot and an arrow button.
- `price`: the white price pill over the BEFORE phone, inside the area no app buttons cover. It pops in at `start`; without one, 3 s before the end. Give it a `start` 2–4 s before the end. Keep it short (about 15 letters): a longer price shrinks to stay off the AFTER.

Leave out any role the user doesn't want. On the first frame everything except the arrow and the price is already there; it settles in the first second, the arrow draws from 0.75 s to 1.35 s, and the phones then drift slowly closer. Start the AFTER on something worth seeing in the first second: that frame is the thumbnail.

**look** options:
- `accent`: colour of the dots and the arrow button, as `#RRGGBB`. Default `#E8663A` (warm orange). Use the brand colour if the user has one.
- `before_label` / `after_label`: the tags on the phones. Default `ӨМНӨ` / `ДАРАА`.

**Auto sound effects** (soft, so they sit under the clip's own sound; raise them with `"sfx": {"volume": 1.5}`): a notification as the comment pill appears, a whoosh as the phones settle, a ding as the price pill lands. If the AFTER clip has its own music, skip extra music.

Before rendering, tell the user the plan in plain words (which clip is before, which is after, the four lines, when the price pops) and ask "OK?". This is the only approval needed.

<!-- audio: this section is copied from core/skill-audio-node.md by build.py; edit it there -->
## Sound effects, voice-over and music

**Sound effects are on by default.** The look adds its own (see "Auto sound effects" above). They are made in code, so there's nothing to license, and they sit quietly under the voice.
- Turn them off: `"sfx": false`. Make them quieter or louder: `"sfx": {"volume": 0.6}`.
- Add one: `"sfx": {"add": [{"sound": "ding", "at": 4.2}]}`. Sounds: whoosh, swish, pop, click, type, shutter, boom, thud, hit, riser, ding, notify, shimmer, paper, tape, marker, projector, tick. `type`, `marker`, `projector` and `riser` also take `"dur"` in seconds; a riser should end on the moment it builds to.
- Let the user hear one render before adding more. Too many sounds feel cheap.

**Voice-over.** If the user wants to talk over the video, ask them to record it on their phone (a voice memo is fine: m4a, mp3 or wav) and copy it into `raw/`. Then add `"voiceover": {"src": "raw/vo.m4a", "at": 0.5}` (`at` = when it starts; optional `"volume"`). While the voice plays, the clips' own sound and the music dip automatically. Run `node SKILL_DIR/scripts/goat.mjs probe raw/vo.m4a` to get its `speech` spans and time the words on screen to them. The clips must add up to at least the voice-over's length (the render warns if not). Recording tips for the user: a small quiet room (a parked car or a wardrobe works), phone about 20 cm from the mouth, read the script out loud once before recording.

**Music.** `"music": {"src": "raw/song.mp3", "volume": 0.25}`. Only use music the user has the rights to. Music added inside the Instagram/TikTok app is the safe choice, so suggest that first.
<!-- /audio -->

## 5. Render and check

`goat render plan.json`

It draws the frame around both clips, mixes the sound and writes the MP4 plus a contact sheet (one frame per second) at `.work-proof-frame/sheet.jpg`. On our test Mac a 6 s video took about 15 s and a 12 s one about 20 s. Run the next render only after the last one ends. Read the contact sheet, the first frame and one full-size frame after the price lands before saying it is done:
`ffmpeg -y -loglevel error -i output/proof-frame.mp4 -frames:v 1 output/check-0.jpg` and the same with `-ss` 1 s before the end (`output/check-1.jpg`).
Check that:
- the first frame (the thumbnail) shows the comment, the headline and both phones;
- the result is clear in the AFTER phone (fix with `cx`/`cy` or `in`), and the price pill doesn't hide what matters in the BEFORE;
- the headline and pills are whole, with no word cut off.

If a render fails twice, stop and explain the error in plain words. Don't loop.

## 6. Hand over

Tell the user where the file is (`output/proof-frame.mp4`) and that it is ready to post. Music can be added in the Instagram/TikTok app.

## Rules

- **Paid ads:** if the user will run this as a paid ad about weight, skin or the body (weight loss, acne, wrinkles, cellulite, body shape), warn them first: Meta restricts before-and-after images for health and cosmetic claims, and the ad may be rejected. Hair, nails, cars and rooms are fine.
- Show the BEFORE as it really was, and the AFTER as the real result. Don't darken, blur or pick a worse BEFORE on purpose, and never put an edited reel or another GOAT video in the AFTER phone.
- A price, phone number or offer goes only in `price`, never in the comment or headline. Never invent a price, number, date or customer name; ask.
- Use only the fonts bundled in `SKILL_DIR/fonts` (Oswald and Inter; they have Ө ө Ү ү). Don't swap in other fonts.
- The output is 1080x1920, 30 fps, H.264, sound normalised to -14 LUFS (Instagram/TikTok level).
