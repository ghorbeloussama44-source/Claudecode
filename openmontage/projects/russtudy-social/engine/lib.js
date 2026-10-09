      // RusStudy social series: shared animation engine, inlined into every episode by scripts/build.py.
      // window.__EP (written by build.py) describes the episode: duration, language, theme and the
      // timed scenes. Everything is deterministic: seeded random numbers, pure functions of time.
      gsap.registerPlugin(CustomEase);
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      const EP = window.__EP;
      const RTL = EP.rtl;
      const SX = RTL ? -1 : 1; // "forwards" along the reading direction

      const $ = (s, r) => (r || document).querySelector(s);
      const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
      function mulberry32(a) {
        return function () {
          a |= 0;
          a = (a + 0x6d2b79f5) | 0;
          let t = Math.imul(a ^ (a >>> 15), 1 | a);
          t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
          return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
      }
      // a tween that calls draw(localTime) on every seek of [t0, t0 + dur]
      function driver(t0, dur, draw) {
        const p = { t: 0 };
        tl.fromTo(p, { t: 0 }, { t: dur, duration: dur, ease: "none", onUpdate: () => draw(p.t) }, t0);
      }

      // ---------------------------------------------------------------- pixel icons
      const PAL = { K: "#0a0a0a", W: "#ffffff", G: "#fbbb21", B: "#2460e8", P: "#a855f7", O: "#f97316", N: "#22c55e", R: "#ef4444", C: "#f0ebe3", Y: "#9cc0ff" };
      function pixelSVG(map, px, pal) {
        const P = Object.assign({}, PAL, pal || {});
        const h = map.length;
        const w = map[0].length;
        let r = "";
        for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
          const c = map[y][x];
          if (c !== ".") r += `<rect x="${x}" y="${y}" width="1.02" height="1.02" fill="${P[c]}"/>`;
        }
        return `<svg width="${w * px}" height="${h * px}" viewBox="0 0 ${w} ${h}" shape-rendering="crispEdges">${r}</svg>`;
      }
      const CHECK = (c, s, w) =>
        `<svg width="${s}" height="${s}" viewBox="0 0 26 26"><path d="M5 13.5l5 5L21 7.5" fill="none" stroke="${c}" stroke-width="${w || 4}" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
      const CHAT = (fill, s, dots) =>
        `<svg width="${s}" height="${s}" viewBox="0 0 24 24"><path d="M12 2.8c-5.1 0-9.2 3.8-9.2 8.5 0 2.4 1.1 4.6 2.9 6.1L5 21.2l4.3-2.2c.9.2 1.8.3 2.7.3 5.1 0 9.2-3.8 9.2-8.5S17.1 2.8 12 2.8z" fill="${fill}"/><circle cx="8" cy="11.3" r="1.4" fill="${dots}"/><circle cx="12" cy="11.3" r="1.4" fill="${dots}"/><circle cx="16" cy="11.3" r="1.4" fill="${dots}"/></svg>`;
      const SEND = (c, s) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24"><path d="M4 12l16-8-6 16-2.6-6.4L4 12z" fill="${c}"/></svg>`;
      const ARROW_DOWN = (c, s) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24"><path d="M12 4v15M6 13l6 6 6-6" fill="none" stroke="${c}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
      const ICONS = {
        plane: ["KK....................", "KWK...................", "KWWK..................", "KWWWKKKKKKKKKKKKKKK...", "KWWWWWWWWWWWWWWWWWWKK.", ".KWWBWWBWWBWWBWWBWWWWK", "..KKKKKWWWWWWWWWWWWWK.", ".......KWWWWWKKKKKKK..", "........KWWWWK........", ".........KWWWK........", "..........KWWK........", "...........KK........."],
        cap: ["........KK........", "......KKWWKK......", "....KKWWWWWWKK....", "..KKWWWWWWWWWWKK..", "KKWWWWWWWWWWWWWWKK", "..KKWWWWWWWWWWKKG.", "....KKWWWWWWKK..G.", "...KKKKKKKKKKKK.G.", "...KKKKKKKKKKKK.GG", "...KKKKKKKKKKKK.GG", "....KKKKKKKKKK...."],
        doc: ["KKKKKKK..", "KWWWWWKK.", "KWKKKWWKK", "KWWWWWWWK", "KWKKKKKWK", "KWWWWWWWK", "KWKKKKKWK", "KWWWWWWWK", "KWKKKWWWK", "KWWWWWWWK", "KKKKKKKKK"],
        pin: ["..KKKKK..", ".KWWWWWK.", "KWWKKKWWK", "KWWKKKWWK", "KWWKKKWWK", ".KWWWWWK.", ".KWWWWWK.", "..KWWWK..", "...KWK...", "....K...."],
        shield: ["....KKKKK....", "..KKWWWWWKK..", ".KWWWWWWWWWK.", ".KWWWWRWWWWK.", ".KWWWWRWWWWK.", ".KWWRRRRRWWK.", ".KWWWWRWWWWK.", ".KWWWWRWWWWK.", "..KWWWWWWWK..", "...KWWWWWK...", "....KWWWK....", ".....KKK....."],
        star: ["...W...", "...W...", "..WWW..", "WWWGWWW", "..WWW..", "...W...", "...W..."],
        coin: ["....KKKK....", "..KKGGGGKK..", ".KGGOOOOGGK.", ".KGOGGGGOGK.", "KGOGWGGGGOGK", "KGOGWGGGGOGK", "KGOGGGGGGOGK", "KGOGGGGGGOGK", ".KGOGGGGOGK.", ".KGGOOOOGGK.", "..KKGGGGKK..", "....KKKK...."],
        key: [".KKKK..........", "KGGGGK.........", "KGKKGGKKKKKKKKK", "KGK.KGGGGGGGGGK", "KGKKGGKKKKGKKGK", "KGGGGK....KK.KK", ".KKKK.........."],
        card: ["KKKKKKKKKKKKKKKK", "KBBBBBBBBBBBBBBK", "KWWWWWWWWWWWWWWK", "KWKKKKWWWWWWWWWK", "KWKYYKWKKKKKKWWK", "KWKYYKWWWWWWWWWK", "KWKKKKWKKKKWWWWK", "KWWWWWWWWWWWWWWK", "KWGGGWWWWWWWWWWK", "KWWWWWWWWWWWWWWK", "KKKKKKKKKKKKKKKK"],
        city: [".......K........", "......KGK.......", ".....KGGGK......", "....KGGGGGK.....", "....KGGGGGK.....", ".....KGGGK......", "..KK..KWK...KK..", ".KWWK.KWK..KWWK.", ".KWWKKKWKKKKWWK.", "KKWWKWWWWWWKWWKK", "KWWWKWBWWBWKWWWK", "KWBWKWWWWWWKWBWK", "KWWWKWBWWBWKWWWK", "KKKKKKKKKKKKKKKK"],
        mic: ["...KKKK...", "..KWWWWK..", "..KWKKWK..", "..KWWWWK..", "..KWKKWK..", "..KWWWWK..", "K.KWWWWK.K", "K..KKKK..K", ".K......K.", "..KK..KK..", "....KK....", "....KK....", "..KKKKKK.."],
        chat: ["..KKKKKKKKKK..", ".KWWWWWWWWWWK.", "KWWWWWWWWWWWWK", "KWKKWWKKWWKKWK", "KWKKWWKKWWKKWK", "KWWWWWWWWWWWWK", ".KWWWWWWWWWWK.", "..KKWWKKKKKK..", "...KWK........", "..KWK.........", "..KK.........."],
      };
      // icon -> svg; mirrored for derja where the icon has a direction (plane, key)
      function icon(name, px, pal) {
        let map = ICONS[name];
        if (RTL && (name === "plane" || name === "key" || name === "chat")) map = map.map((r) => r.split("").reverse().join(""));
        return pixelSVG(map, px, pal);
      }
      $$("[data-icon]").forEach((el) => {
        const pal = el.dataset.pal ? JSON.parse(el.dataset.pal) : null;
        el.innerHTML = icon(el.dataset.icon, +el.dataset.px, pal);
      });
      $$("[data-check]").forEach((el) => (el.innerHTML = CHECK(el.dataset.check, +el.dataset.s, +el.dataset.w || 4)));
      $$("[data-chat]").forEach((el) => (el.innerHTML = CHAT(el.dataset.chat, +el.dataset.s, el.dataset.dots || "#fff")));
      $$("[data-send]").forEach((el) => (el.innerHTML = SEND(el.dataset.send, +el.dataset.s)));
      $$("[data-down]").forEach((el) => (el.innerHTML = ARROW_DOWN(el.dataset.down, +el.dataset.s)));

      // ---------------------------------------------------------------- shared moves
      const words = (el) => $$(".w", el);
      function revealWords(el, t, st, dur) {
        const w = words(el);
        if (w.length) tl.fromTo(w, { yPercent: 118 }, { yPercent: 0, duration: dur || 0.62, ease: "expo.out", stagger: st || 0.06 }, t);
      }
      function popIn(el, t, from) {
        tl.fromTo(el, { scale: from || 0.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.5, ease: "back.out(2.2)" }, t);
      }
      function slideIn(el, t, dy, dur) {
        tl.fromTo(el, { y: dy || 70, opacity: 0 }, { y: 0, opacity: 1, duration: dur || 0.6, ease: "expo.out" }, t);
      }
      function sideIn(el, t, dx) {
        tl.fromTo(el, { x: -SX * (dx || 60), opacity: 0 }, { x: 0, opacity: 1, duration: 0.55, ease: "expo.out" }, t);
      }
      // content leaves upwards in the last 0.3 s of its scene
      function exitUp(els, t) {
        tl.to(els, { y: -60, opacity: 0, duration: 0.28, ease: "power2.in", stagger: 0.025 }, t);
      }
      function bob(el, t0, dur, amp, period, phase) {
        driver(t0, dur, (t) => gsap.set(el, { y: amp * Math.sin((t / period) * Math.PI * 2 + (phase || 0)) }));
      }

      // ---------------------------------------------------------------- ambient background
      function ambient() {
        const cv = $("#amb-c");
        const ctx = cv.getContext("2d");
        const W = 1080;
        const H = 1920;
        const rng = mulberry32(EP.seed);
        const theme = EP.theme;
        if (theme === "night") {
          const stars = Array.from({ length: 70 }, () => ({ x: rng() * W, y: rng() * 1500, r: 1 + rng() * 2.4, f: 0.6 + rng() * 1.6, p: rng() * 6.28 }));
          const snow = Array.from({ length: 46 }, () => ({ x: rng() * W, y: rng() * H, r: 2 + rng() * 4, v: 40 + rng() * 70, a: rng() * 6.28, d: 10 + rng() * 26 }));
          // pixel skyline along the bottom (behind the platform captions)
          const bld = [];
          let x = -10;
          while (x < W) {
            const w = 60 + Math.floor(rng() * 5) * 20;
            const h = 160 + Math.floor(rng() * 9) * 26;
            const win = [];
            for (let wy = H - h + 26; wy < H - 30; wy += 34) for (let wx = x + 14; wx < x + w - 18; wx += 26) if (rng() < 0.32) win.push([wx, wy, rng() * 6.28]);
            bld.push({ x, w, h, win });
            x += w + 6;
          }
          driver(0, EP.D, (t) => {
            const g = ctx.createLinearGradient(0, 0, 0, H);
            g.addColorStop(0, "#0a1433");
            g.addColorStop(0.55, "#12276b");
            g.addColorStop(1, "#1d3f9e");
            ctx.fillStyle = g;
            ctx.fillRect(0, 0, W, H);
            for (const s of stars) {
              ctx.globalAlpha = 0.35 + 0.65 * (0.5 + 0.5 * Math.sin(t * s.f * 2 + s.p));
              ctx.fillStyle = "#ffffff";
              ctx.fillRect(Math.round(s.x), Math.round(s.y), s.r, s.r);
            }
            ctx.globalAlpha = 1;
            for (const b of bld) {
              ctx.fillStyle = "#081030";
              ctx.fillRect(b.x, H - b.h, b.w, b.h);
              for (const w of b.win) {
                ctx.globalAlpha = 0.55 + 0.45 * (Math.sin(t * 0.7 + w[2]) > -0.6 ? 1 : 0.2);
                ctx.fillStyle = "#fbbb21";
                ctx.fillRect(w[0], w[1], 10, 14);
              }
              ctx.globalAlpha = 1;
            }
            ctx.fillStyle = "#ffffff";
            for (const s of snow) {
              const y = (s.y + s.v * t) % (H + 20);
              const xx = s.x + s.d * Math.sin(t * 0.8 + s.a);
              ctx.globalAlpha = 0.5;
              ctx.fillRect(Math.round(xx), Math.round(y), s.r, s.r);
            }
            ctx.globalAlpha = 1;
          });
        } else if (theme === "cream") {
          const cols = ["#a855f7", "#2460e8", "#fbbb21", "#f97316", "#22c55e"];
          const px = Array.from({ length: 26 }, () => ({ x: rng() * W, y: rng() * H, s: 12 + Math.floor(rng() * 3) * 8, c: cols[Math.floor(rng() * cols.length)], v: 12 + rng() * 26, p: rng() * 6.28 }));
          driver(0, EP.D, (t) => {
            ctx.fillStyle = "#f0ebe3";
            ctx.fillRect(0, 0, W, H);
            ctx.fillStyle = "rgba(10,10,10,0.055)";
            const off = (t * 10) % 72;
            for (let gx = 36; gx < W; gx += 72) ctx.fillRect(gx, 0, 2, H);
            for (let gy = -72 + off; gy < H; gy += 72) ctx.fillRect(0, gy, W, 2);
            for (const p of px) {
              const y = (((p.y - p.v * t) % (H + 60)) + H + 60) % (H + 60) - 30;
              ctx.globalAlpha = 0.22 + 0.1 * Math.sin(t * 1.3 + p.p);
              ctx.fillStyle = p.c;
              ctx.fillRect(Math.round(p.x), Math.round(y), p.s, p.s);
            }
            ctx.globalAlpha = 1;
          });
        } else {
          const dust = Array.from({ length: 60 }, () => ({ x: rng() * W, y: rng() * H, r: 2 + rng() * 3, v: 8 + rng() * 22, p: rng() * 6.28 }));
          driver(0, EP.D, (t) => {
            ctx.fillStyle = "#0a0a0a";
            ctx.fillRect(0, 0, W, H);
            const gx = RTL ? 700 : 380;
            const g = ctx.createRadialGradient(gx, 640, 20, gx, 640, 900);
            g.addColorStop(0, "rgba(251,187,33,0.16)");
            g.addColorStop(1, "rgba(251,187,33,0)");
            ctx.fillStyle = g;
            ctx.fillRect(0, 0, W, H);
            ctx.fillStyle = "rgba(255,255,255,0.07)";
            for (let yy = 48; yy < H; yy += 48) for (let xx = 24; xx < W; xx += 48) ctx.fillRect(xx, yy, 3, 3);
            ctx.fillStyle = "#fbbb21";
            for (const d of dust) {
              const y = (((d.y - d.v * t) % H) + H) % H;
              ctx.globalAlpha = 0.25 + 0.25 * Math.sin(t * 1.7 + d.p);
              ctx.fillRect(Math.round(d.x), Math.round(y), d.r, d.r);
            }
            ctx.globalAlpha = 1;
          });
        }
      }

      // ---------------------------------------------------------------- chrome: brand pill, series pill, progress
      function chrome() {
        tl.fromTo("#brand", { y: -30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "expo.out" }, 0.05);
        const h = EP.scenes[0];
        const tSeries = h.type === "hook" ? h.t0 + h.dur + 0.1 : 0.2;
        tl.fromTo("#series", { y: -20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "expo.out" }, tSeries);
        tl.fromTo("#prog", { opacity: 0 }, { opacity: 1, duration: 0.3 }, tSeries);
        tl.fromTo("#progf", { scaleX: 0 }, { scaleX: 1, duration: EP.D, ease: "none" }, 0);
      }

      // ---------------------------------------------------------------- scene animators
      const A = {};
      A.hook = (sec, s) => {
        const t0 = s.t0;
        tl.fromTo($(".hk-k .kick", sec), { y: -24, opacity: 0 }, { y: 0, opacity: 1, duration: 0.42, ease: "power3.out" }, t0 + 0.04);
        tl.fromTo($(".hk-ic .pix", sec), { scale: 0, rotation: -18 * SX }, { scale: 1, rotation: 0, duration: 0.55, ease: "back.out(2.4)" }, t0 + 0.1);
        bob($(".hk-ic", sec), t0 + 0.6, s.dur - 0.65, 8, 1.6);
        revealWords($(".hk-t", sec), t0 + 0.12, 0.055, 0.6);
        const ul = $(".hk-ul", sec);
        if (ul) tl.fromTo(ul, { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "expo.inOut" }, t0 + 0.75);
        const deco = $(".hk-deco", sec);
        tl.fromTo(deco, { rotation: -26 * SX, scale: 0.85 }, { rotation: -12 * SX, scale: 1, duration: s.dur + 0.4, ease: "power1.out" }, t0);
        // the coloured page lifts off upwards and uncovers the series background
        const tx = t0 + s.dur - 0.05;
        tl.to([$(".hk-k", sec), $(".hk-ic", sec), $(".hk-t", sec), ul].filter(Boolean), { y: -120, duration: 0.45, ease: "power3.in" }, tx);
        tl.fromTo(sec, { clipPath: "inset(0px 0px 0px 0px)" }, { clipPath: "inset(0px 0px 1920px 0px)", duration: 0.48, ease: "power3.inOut" }, tx);
      };

      A.question = (sec, s) => {
        const t0 = s.t0;
        popIn($(".q-lab .pill", sec), t0 + 0.05, 0.6);
        tl.fromTo($$(".q-dots i", sec), { scale: 0 }, { scale: 1, duration: 0.3, ease: "back.out(3)", stagger: 0.05 }, t0 + 0.2);
        revealWords($(".q-t", sec), t0 + 0.12, 0.05, 0.62);
        const ans = $(".q-ans", sec);
        slideIn(ans, t0 + 0.85, 80, 0.6);
        // the answer is spoken: ring pulses around the mic, the waveform moves (pseudo-random, seeded)
        const ring = $(".q-ring", sec);
        tl.fromTo(ring, { scale: 1, opacity: 0.8 }, { scale: 1.35, opacity: 0, duration: 1.1, ease: "power2.out", repeat: Math.floor((s.dur - 2) / 1.1) }, t0 + 1.2);
        const bars = $$(".q-wave i", sec);
        const rng = mulberry32(EP.seed + s.i * 97);
        const ph = bars.map(() => [rng() * 6.28, 3 + rng() * 5, rng() * 6.28, 7 + rng() * 6, 0.35 + rng() * 0.65]);
        driver(t0 + 0.85, s.dur - 1.1, (t) => {
          const on = Math.min(1, t / 0.6);
          bars.forEach((b, k) => {
            const p = ph[k];
            const env = 0.55 + 0.45 * Math.sin(t * 1.9 + k * 0.35);
            const v = Math.abs(0.6 * Math.sin(t * p[1] + p[0]) + 0.4 * Math.sin(t * p[3] + p[2])) * p[4] * env;
            gsap.set(b, { scaleY: 0.08 + 0.92 * v * on });
          });
        });
        exitUp([$(".q-lab", sec), $(".q-t", sec), ans], t0 + s.dur - 0.32);
      };

      A.week = (sec, s) => {
        // persistent strip over the "day" scenes: cells drop in once, the highlight moves day by day
        const cells = $$(".wk-d", sec);
        tl.fromTo(cells, { y: -40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "expo.out", stagger: 0.04 }, s.t0 + 0.02);
        s.days.forEach((d, k) => {
          const c = cells[d.n - 1];
          tl.fromTo($(".wk-hl", c), { scale: 0 }, { scale: 1, duration: 0.42, ease: "back.out(2)" }, d.t0 + 0.12);
          const base = getComputedStyle(c).color;
          tl.to($$(".wk-tx", c), { color: "#0a0a0a", duration: 0.2 }, d.t0 + 0.14);
          const nx = s.days[k + 1];
          if (nx) {
            tl.to($(".wk-hl", c), { scale: 0, duration: 0.3, ease: "power2.in" }, nx.t0 - 0.05);
            tl.to($$(".wk-tx", c), { color: base, duration: 0.2 }, nx.t0 - 0.05);
            tl.fromTo($(".wk-ok", c), { scale: 0 }, { scale: 1, duration: 0.35, ease: "back.out(3)" }, nx.t0 + 0.05);
          }
        });
        exitUp(cells, s.t0 + s.dur - 0.32);
      };

      A.day = (sec, s) => {
        const t0 = s.t0;
        slideIn($(".dy-l", sec), t0 + 0.05, 30, 0.45);
        tl.fromTo($(".dy-n .num .w", sec), { yPercent: 105 }, { yPercent: 0, duration: 0.7, ease: "expo.out" }, t0 + 0.1);
        tl.fromTo($(".dy-n .pix", sec), { scale: 0, rotation: 20 * SX }, { scale: 1, rotation: 0, duration: 0.6, ease: "back.out(2.2)" }, t0 + 0.3);
        bob($(".dy-n .pix", sec), t0 + 0.9, s.dur - 1.2, 10, 1.8);
        revealWords($(".dy-t", sec), t0 + 0.32, 0.07, 0.62);
        exitUp([$(".dy-l", sec), $(".dy-n", sec), $(".dy-t", sec)], t0 + s.dur - 0.32);
      };

      CustomEase.create("odoRoll", "M0,0 C0.08,0.42 0.24,0.86 0.5,0.97 0.7,1.01 0.86,1.003 1,1");
      A.price = (sec, s) => {
        const t0 = s.t0;
        tl.fromTo($(".pr-k .kick", sec), { opacity: 0, y: -24 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, t0 + 0.05);
        sideIn($(".pr-des", sec), t0 + 0.1, 50);
        tl.fromTo($(".pr-deco", sec), { rotation: -30 * SX, opacity: 0 }, { rotation: -12 * SX, opacity: 1, duration: 2.0, ease: "power2.out" }, t0);
        tl.fromTo($(".pr-cur", sec), { opacity: 0, rotation: -40 * SX, scale: 0.4 }, { opacity: 1, rotation: 0, scale: 1, duration: 0.5, ease: "back.out(2)" }, t0 + 0.7);
        const cols = $$(".odo-col", sec);
        const digits = s.digits;
        cols.forEach((col, i) => {
          let html = "";
          for (let k = 0; k < 40; k++) html += `<div>${k % 10}</div>`;
          col.innerHTML = html;
          const startIdx = 3 + i * 2;
          const endIdx = 20 + digits[i] + (i % 2) * 10;
          const land = t0 + 0.86 + i * 0.06;
          const h = 1.1 * s.num_size; // one digit cell (.odo-col div: 1.1em)
          tl.fromTo(col, { y: -startIdx * h }, { y: -endIdx * h, duration: land - (t0 + 0.15), ease: "odoRoll" }, t0 + 0.15);
        });
        tl.fromTo($(".pr-num", sec), { scale: 1 }, { keyframes: [{ scale: 1.04, duration: 0.06, ease: "power2.out" }, { scale: 1, duration: 0.3, ease: "elastic.out(1, 0.45)" }] }, t0 + 1.12);
        tl.fromTo($(".pr-pill .pill", sec), { scale: 0, rotation: 12 * SX }, { scale: 1, rotation: -2 * SX, duration: 0.42, ease: "back.out(2.4)" }, t0 + 1.35);
        exitUp([$(".pr-k", sec), $(".pr-des", sec), $(".pr-row", sec), $(".pr-pill", sec)], t0 + s.dur - 0.32);
        tl.to($(".pr-deco", sec), { opacity: 0, duration: 0.3 }, t0 + s.dur - 0.32);
      };

      function stampIn(el, t, rot) {
        tl.fromTo(el, { scale: 2.6, rotation: rot - 14, opacity: 0 }, { scale: 1, rotation: rot, opacity: 0.94, duration: 0.13, ease: "power4.in" }, t - 0.13);
        tl.to(el, { keyframes: [{ scale: 0.94, duration: 0.04 }, { scale: 1, duration: 0.28, ease: "elastic.out(1.2, 0.4)" }] }, t);
      }
      function shake(el, t, a) {
        tl.to(el, { keyframes: [{ x: -a, y: a * 0.6, duration: 0.03 }, { x: a * 0.8, y: -a * 0.5, duration: 0.04 }, { x: -a * 0.4, y: a * 0.25, duration: 0.04 }, { x: 0, y: 0, duration: 0.06 }] }, t);
      }
      A.receipt = (sec, s) => {
        const t0 = s.t0;
        const paper = $(".rc-paper", sec);
        tl.fromTo(paper, { y: 1300, rotation: 3 * SX }, { y: 0, rotation: 0, duration: 0.7, ease: "expo.out" }, t0 + 0.02);
        const inc = $$(".rc-l.inc", sec);
        inc.forEach((l, i) => {
          const t = t0 + 0.9 + i * 0.95;
          tl.fromTo(l, { opacity: 0, x: -SX * 30 }, { opacity: 1, x: 0, duration: 0.35, ease: "power3.out" }, t);
          tl.fromTo($(".ok", l), { scale: 0 }, { scale: 1, duration: 0.35, ease: "back.out(3)" }, t + 0.18);
        });
        const tTot = t0 + 0.9 + inc.length * 0.95 + 0.2;
        tl.fromTo([$(".rc-div", sec), $(".rc-tot", sec)], { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out", stagger: 0.08 }, tTot);
        tl.fromTo($(".rc-tot .b", sec), { scale: 0.7 }, { scale: 1, duration: 0.5, ease: "back.out(2.5)" }, tTot + 0.1);
        const st = $(".stamp", sec);
        stampIn(st, tTot + 0.95, -9 * SX);
        shake(paper, tTot + 0.95, 9);
        const tOpt = tTot + 1.9;
        tl.fromTo($(".rc-oh", sec), { opacity: 0 }, { opacity: 1, duration: 0.3 }, tOpt);
        $$(".rc-o", sec).forEach((l, i) => tl.fromTo(l, { opacity: 0, x: -SX * 30 }, { opacity: 1, x: 0, duration: 0.35, ease: "power3.out" }, tOpt + 0.4 + i * 0.6));
        exitUp([paper, st], t0 + s.dur - 0.32);
      };

      function listScene(sec, s, gap) {
        const t0 = s.t0;
        const items = $$(".ls-i", sec);
        const fill = $(".ls-fill", sec);
        const line = $(".ls-line", sec);
        if (line) tl.fromTo(line, { opacity: 0 }, { opacity: 1, duration: 0.4 }, t0 + 0.1);
        items.forEach((it, i) => {
          const t = t0 + 0.3 + i * gap;
          const mark = $(".ls-n", it) || $(".ls-ic", it);
          popIn(mark, t, 0.3);
          const f = $(".ls-n .f", it);
          if (f) tl.fromTo(f, { scale: 0 }, { scale: 1, duration: 0.35, ease: "back.out(2)" }, t + 0.1);
          if (f) tl.to($(".ls-n span", it), { color: "#0a0a0a", duration: 0.2 }, t + 0.15);
          tl.fromTo($$(".ls-tx > *", it), { opacity: 0, x: -SX * 50 }, { opacity: 1, x: 0, duration: 0.55, ease: "expo.out", stagger: 0.1 }, t + 0.08);
          if (fill && i > 0) tl.to(fill, { scaleY: i / (items.length - 1), duration: 0.5, ease: "power2.inOut" }, t - 0.3);
          if (i > 0) {
            const prev = items[i - 1];
            tl.to($$(".ls-tx > *", prev), { opacity: 0.42, duration: 0.4 }, t);
          }
        });
        exitUp(items, t0 + s.dur - 0.34);
        if (line) tl.to(line, { opacity: 0, duration: 0.25 }, t0 + s.dur - 0.32);
      }
      A.steps = (sec, s) => listScene(sec, s, s.gap);
      A.points = (sec, s) => listScene(sec, s, s.gap);

      A.checklist = (sec, s) => {
        const t0 = s.t0;
        const card = $(".ck-card", sec);
        slideIn(card, t0 + 0.02, 160, 0.65);
        const items = $$(".ck-i", sec);
        tl.fromTo(items, { opacity: 0, x: -SX * 40 }, { opacity: 1, x: 0, duration: 0.45, ease: "expo.out", stagger: 0.12 }, t0 + 0.35);
        items.forEach((it, i) => {
          const t = t0 + 1.1 + i * 1.9;
          tl.fromTo($(".ck-b .f", it), { scale: 0 }, { scale: 1, duration: 0.3, ease: "back.out(2.6)" }, t);
          tl.fromTo($(".ck-b path", it), { strokeDashoffset: 30 }, { strokeDashoffset: 0, duration: 0.3, ease: "power2.out" }, t + 0.12);
          tl.fromTo($(".ck-t", it), { scale: 1 }, { keyframes: [{ scale: 1.06, duration: 0.1 }, { scale: 1, duration: 0.3, ease: "back.out(3)" }] }, t + 0.05);
        });
        const note = $(".ck-note", sec);
        slideIn(note, t0 + 1.1 + items.length * 1.9 + 0.3, 60, 0.6);
        exitUp([card, note], t0 + s.dur - 0.32);
      };

      A.chat = (sec, s) => {
        const t0 = s.t0;
        const ph = $(".ph", sec);
        tl.fromTo(ph, { y: 1200, rotation: -4 * SX }, { y: 0, rotation: 0, duration: 0.75, ease: "expo.out" }, t0 + 0.02);
        const out = $(".bub.out", sec);
        const bubIn = (el, t) => {
          tl.fromTo(el, { scale: 0.3, opacity: 0, transformOrigin: RTL ? "100% 0%" : "0% 0%" }, { scale: 1, opacity: 1, duration: 0.42, ease: "back.out(1.8)" }, t);
        };
        tl.fromTo(out, { scale: 0.3, opacity: 0, transformOrigin: RTL ? "0% 100%" : "100% 100%" }, { scale: 1, opacity: 1, duration: 0.42, ease: "back.out(1.8)" }, t0 + 0.8);
        // ticks turn blue (read)
        tl.to($$(".bub.out .tk path", sec), { stroke: "#2c9cf0", duration: 0.2 }, t0 + 1.7);
        // typing... then the first answer
        const typ = $(".typ", sec);
        tl.fromTo(typ, { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }, t0 + 1.9);
        $$(".typ i", sec).forEach((d, k) => tl.fromTo(d, { y: 0 }, { y: -8, duration: 0.22, ease: "sine.inOut", yoyo: true, repeat: 5, delay: 0 }, t0 + 2.0 + k * 0.12));
        tl.to(typ, { opacity: 0, duration: 0.15 }, t0 + 3.4);
        bubIn($(".bub.in1", sec), t0 + 3.45);
        bubIn($(".wcard", sec), t0 + 5.6);
        tl.fromTo($(".wcard .bt", sec), { backgroundColor: "rgba(168,85,247,0)" }, { backgroundColor: "rgba(168,85,247,0.12)", duration: 0.3, yoyo: true, repeat: 3 }, t0 + 6.4);
        bubIn($(".bub.in2", sec), t0 + 8.6);
        exitUp([ph], t0 + s.dur - 0.32);
      };

      A.recap = (sec, s) => {
        const t0 = s.t0;
        const its = $$(".rp-i", sec);
        const ars = $$(".rp-ar", sec);
        its.forEach((it, i) => {
          sideIn(it, t0 + 0.08 + i * 0.55, 80);
          if (ars[i]) tl.fromTo(ars[i], { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }, t0 + 0.4 + i * 0.55);
        });
        tl.to(its[its.length - 1], { keyframes: [{ scale: 1.05, duration: 0.12 }, { scale: 1, duration: 0.35, ease: "back.out(3)" }] }, t0 + 0.08 + (its.length - 1) * 0.55 + 0.6);
        exitUp([...its, ...ars], t0 + s.dur - 0.32);
      };

      function fmtNum(v, sep) {
        const s = String(Math.round(v));
        return s.replace(/\B(?=(\d{3})+(?!\d))/g, sep);
      }
      A.stats = (sec, s) => {
        const t0 = s.t0;
        $$(".st", sec).forEach((st, i) => {
          const t = t0 + 0.15 + i * s.gap;
          slideIn(st, t, 80, 0.6);
          const num = $(".num", st);
          const target = +num.dataset.v;
          const sep = num.dataset.sep;
          const c = { v: 0 };
          tl.fromTo(c, { v: 0 }, { v: target, duration: 1.1, ease: "power3.out", onUpdate: () => (num.textContent = fmtNum(c.v, sep)) }, t + 0.1);
          tl.fromTo($(".st-bar", st), { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "expo.out" }, t + 0.5);
        });
        exitUp($$(".st", sec), t0 + s.dur - 0.32);
      };

      A.chips = (sec, s) => {
        const t0 = s.t0;
        $$(".chs .pill", sec).forEach((p, i) => {
          tl.fromTo(p, { scale: 0, rotation: (i ? 6 : -6) * SX }, { scale: 1, rotation: (i ? 1.5 : -1.5) * SX, duration: 0.5, ease: "back.out(2.2)" }, t0 + 0.1 + i * 0.5);
          tl.fromTo($(".ok", p), { scale: 0 }, { scale: 1, duration: 0.35, ease: "back.out(3)" }, t0 + 0.35 + i * 0.5);
        });
        exitUp($$(".chs .pill", sec), t0 + s.dur - 0.32);
      };

      A.cta = (sec, s) => {
        const t0 = s.t0;
        tl.fromTo($(".cta-bg", sec), { opacity: 0 }, { opacity: 1, duration: 0.35, ease: "power1.out" }, t0);
        tl.fromTo($(".cta-wm .wm", sec), { yPercent: 110, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.7, ease: "expo.out" }, t0 + 0.1);
        slideIn($(".cta-tag", sec), t0 + 0.35, 30, 0.5);
        slideIn($(".cta-wa", sec), t0 + 0.6, 90, 0.7);
        tl.fromTo($(".cta-wa .ic", sec), { scale: 0, rotation: -30 * SX }, { scale: 1, rotation: 0, duration: 0.5, ease: "back.out(2.5)" }, t0 + 0.85);
        slideIn($(".cta-web", sec), t0 + 0.95, 40, 0.5);
        tl.fromTo($(".cta-chip .pill", sec), { scale: 0, rotation: 8 * SX }, { scale: 1, rotation: -2 * SX, duration: 0.45, ease: "back.out(2.4)" }, t0 + 1.25);
        slideIn($(".cta-bio", sec), t0 + 1.5, 40, 0.5);
        // gentle attention loop on the WhatsApp card and the link-in-bio arrow until the end
        const n = Math.floor((s.dur - 2.4) / 1.2);
        if (n > 0) tl.to($(".cta-wa", sec), { scale: 1.035, duration: 0.6, ease: "sine.inOut", yoyo: true, repeat: n * 2 - 1 }, t0 + 2.1);
        bob($(".cta-bio .arr", sec), t0 + 2.0, s.dur - 2.0, 6, 0.8);
      };

      // ---------------------------------------------------------------- build the timeline
      ambient();
      chrome();
      for (const s of EP.scenes) A[s.type]($("#" + s.id), s);
      if (EP.week) A.week($("#wk"), EP.week);
      tl.set({}, {}, EP.D);
      window.__timelines["main"] = tl;
