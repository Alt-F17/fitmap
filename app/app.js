// FitMap: user-reported phone accessory cross-compatibility.
// Data: data.json (built by pipeline/build.py). No framework, no backend.

const I18N = {
  fr: {
    skip: "Aller au contenu", modePhone: "Téléphone client", modeStock: "Accessoire",
    modeGrid: "Tableau", brandAll: "Toutes marques",
    phPhone: "Téléphone du client (ex. S25 FE)",
    phStock: "Accessoire fait pour… (ex. A57)",
    disclaimer: "Basé sur des rapports d'utilisateurs, pas sur des garanties du fabricant. Vérifiez l'ajustement avant que le client parte.",
    fitsThis: "Accessoires d'autres téléphones qui vont sur le", fitsOthers: "Un accessoire fait pour le",
    goesOn: "va aussi sur…", madeFor: "Fait pour", worksOn: "Va sur",
    reports: (n) => `${n} rapport${n > 1 ? "s" : ""}`,
    none: "Aucun rapport d'utilisateur pour l'instant.",
    noneBrand: (b) => `Aucun rapport spécifique à ${b}. `, showAll: "Voir toutes les marques",
    noneHint: "Pas de rapport ≠ incompatible. Essayez en magasin et signalez le résultat.",
    report: "Signaler un essai", homeTitle: "Trouvez ce qui va, selon de vrais utilisateurs",
    homeSub: "Tapez le téléphone du client. On vous montre les protecteurs, étuis et anneaux faits pour d'autres modèles que les utilisateurs disent compatibles.",
    popular: "Recherches fréquentes", universal: "Accessoires universels (anneaux MagSafe/Qi2, etc.)",
    v: { fits: "Compatible", fits_with_caveat: "Compatible, avec réserve", doesnt_fit: "Incompatible", mixed: "Avis partagés" },
    k: { strong: "Fiable", likely: "Probable", weak: "Peu de preuves", mixed: "Contradictoire" },
    sources: "Sources", open: "Voir la source", firsthand: "Essai personnel", secondhand: "Ouï-dire",
    src: { reddit_comment: "Reddit", reddit_post: "Reddit", reddit_excerpt: "Reddit", review_bestbuy: "Avis Best Buy", review_tuff8: "Avis TUFF8", store_test: "Testé en magasin" },
    family: "Famille", category: "Catégorie", gridHint: "Lignes : fait pour · Colonnes : utilisé sur. Touchez une case pour les sources.",
    reportTitle: "Signaler un essai", reportIntro: "Vous avez essayé un accessoire sur un autre téléphone? Remplissez, puis partagez le texte avec le responsable de l'outil.",
    accFor: "Accessoire fait pour", putOn: "Mis sur", result: "Résultat", brandLbl: "Marque (AXS, TUFF8…)",
    notes: "Détails (coins, caméra, boutons…)", share: "Partager", copy: "Copier", copied: "Copié!",
    updated: (d, n) => `Données du ${d} · ${n} sources`, back: "Retour", all: "Tout",
    universalOn: "Universel",
    fallback: (b) => `Aucun utilisateur n'a encore rapporté un accessoire ${b} sur un autre modèle. Voici les rapports toutes marques : l'ajustement dépend surtout de la forme du téléphone, donc un ${b} fait pour le même modèle se comporte en général pareil. Vérifiez en magasin.`,
  },
  en: {
    skip: "Skip to content", modePhone: "Customer phone", modeStock: "Accessory",
    modeGrid: "Grid", brandAll: "All brands",
    phPhone: "Customer's phone (e.g. S25 FE)",
    phStock: "Accessory made for… (e.g. A57)",
    disclaimer: "Based on user reports, not manufacturer guarantees. Check the fit before the customer leaves.",
    fitsThis: "Accessories from other phones that fit the", fitsOthers: "An accessory made for the",
    goesOn: "also fits…", madeFor: "Made for", worksOn: "Fits",
    reports: (n) => `${n} report${n > 1 ? "s" : ""}`,
    none: "No user reports yet.",
    noneBrand: (b) => `No ${b}-specific reports. `, showAll: "Show all brands",
    noneHint: "No reports ≠ doesn't fit. Try it in store and report the result.",
    report: "Report a fit", homeTitle: "Find what fits, according to real users",
    homeSub: "Type the customer's phone. We show protectors, cases and rings made for other models that users say fit.",
    popular: "Common searches", universal: "Universal add-ons (MagSafe/Qi2 rings, etc.)",
    v: { fits: "Fits", fits_with_caveat: "Fits, with a catch", doesnt_fit: "Doesn't fit", mixed: "Mixed reports" },
    k: { strong: "Strong", likely: "Likely", weak: "Thin evidence", mixed: "Conflicting" },
    sources: "Sources", open: "Open source", firsthand: "Tried it", secondhand: "Hearsay",
    src: { reddit_comment: "Reddit", reddit_post: "Reddit", reddit_excerpt: "Reddit", review_bestbuy: "Best Buy review", review_tuff8: "TUFF8 review", store_test: "Store-tested" },
    family: "Family", category: "Category", gridHint: "Rows: made for · Columns: used on. Tap a cell for sources.",
    reportTitle: "Report a fit", reportIntro: "Tried an accessory on a different phone? Fill this in, then share the text with the tool's maintainer.",
    accFor: "Accessory made for", putOn: "Put on", result: "Result", brandLbl: "Brand (AXS, TUFF8…)",
    notes: "Details (corners, camera, buttons…)", share: "Share", copy: "Copy", copied: "Copied!",
    updated: (d, n) => `Data from ${d} · ${n} sources`, back: "Back", all: "All",
    universalOn: "Universal",
    fallback: (b) => `No user has reported a ${b} accessory on a different model yet. Showing all-brand reports instead: fit mostly comes from the phone's shape, so a ${b} item made for the same model usually behaves the same. Check in store.`,
  },
};
const CATS = {
  screen_protector: { fr: "Protecteur d'écran", en: "Screen protector", icon: "▭" },
  privacy_protector: { fr: "Protecteur confidentialité", en: "Privacy protector", icon: "◩" },
  camera_lens_protector: { fr: "Protège-lentille", en: "Camera lens protector", icon: "◎" },
  case: { fr: "Étui", en: "Case", icon: "▢" },
  folio_wallet_case: { fr: "Étui folio / portefeuille", en: "Folio / wallet case", icon: "▤" },
  magsafe_ring: { fr: "Anneau MagSafe / Qi2", en: "MagSafe / Qi2 ring", icon: "◯" },
  magnetic_accessory: { fr: "Accessoire magnétique", en: "Magnetic accessory", icon: "⊕" },
  other: { fr: "Autre", en: "Other", icon: "•" },
};
const CAVEATS = {
  camera_cutout_larger: ["Découpe caméra plus grande", "Camera cutout larger"],
  camera_exposed: ["Caméra moins protégée", "Camera less protected"],
  camera_lip_too_low: ["Rebord caméra trop bas", "Camera lip too low"],
  button_misaligned: ["Boutons décalés", "Buttons misaligned"],
  port_misaligned: ["Port décalé", "Port misaligned"],
  speaker_misaligned: ["Haut-parleur décalé", "Speaker misaligned"],
  corners_lift: ["Coins qui lèvent", "Corners lift"],
  edges_dont_cover: ["Bords non couverts", "Edges not covered"],
  sensor_or_fingerprint_issue: ["Capteur / empreinte gêné", "Sensor / fingerprint issue"],
  selfie_cam_cutout_off: ["Découpe selfie décalée", "Selfie cutout off"],
  loose_fit: ["Un peu lâche", "Slightly loose"],
  tight_fit: ["Serré", "Tight fit"],
  slider_or_key_hole_missing: ["Pas de trou pour la touche", "No hole for key/slider"],
  magnet_weak_or_offset: ["Aimant faible / décalé", "Magnet weak / offset"],
  case_conflicts_with_protector: ["Conflit étui / protecteur", "Case vs protector conflict"],
  s_pen_or_stylus_issue: ["Problème stylet", "Stylus issue"],
  hinge_issue: ["Problème charnière", "Hinge issue"],
  other: ["Autre réserve", "Other catch"],
};
const VERDICT_ICON = { fits: "✓", fits_with_caveat: "!", doesnt_fit: "✕", mixed: "≈" };
const VRANK = { fits: 0, fits_with_caveat: 1, mixed: 2, doesnt_fit: 3 };
const KRANK = { strong: 0, likely: 1, mixed: 2, weak: 3 };
const POPULAR = ["s25fe", "a57", "ip17promax", "ip18promax", "s26u", "mg25", "a36", "ip16", "tcl60xe", "razr25"];

const state = {
  lang: localStorage.getItem("lang") || "fr",
  brand: localStorage.getItem("brand") || "all",
  data: null, dev: new Map(), byUsedOn: new Map(), byFor: new Map(), searchIdx: [],
};
const $ = (s, el = document) => el.querySelector(s);
const t = (k) => I18N[state.lang][k];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const catLabel = (c) => CATS[c]?.[state.lang] || c;
const devName = (id) => (id === "universal" ? t("universalOn") : state.dev.get(id)?.n || id);
const norm = (s) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "")
  .replace(/galaxy|samsung|apple|motorola|\bmoto\b|iphone|tcl|[()]/g, " ")
  .replace(/\bplus\b/g, "+").replace(/\s+/g, "");

// ---------- data ----------
async function load() {
  const res = await fetch("data.json", { cache: "no-cache" }).catch(() => fetch("data.json"));
  const data = await res.json();
  state.data = data;
  for (const d of data.devices) {
    state.dev.set(d.id, d);
    const keys = new Set([d.n, ...d.a].map(norm).filter(Boolean));
    state.searchIdx.push({ id: d.id, keys: [...keys], label: d.n, fam: d.f, y: d.y });
  }
  for (const e of data.edges) {
    push(state.byUsedOn, e.u, e);
    push(state.byFor, e.f, e);
  }
  $("#meta").textContent = t("updated")(data.generated, data.stats.sources);
}
const push = (m, k, v) => (m.get(k) || m.set(k, []).get(k)).push(v);

function scoreFor(edge) {
  return state.brand === "all" || state.fallback ? edge.s.all : edge.s[state.brand] || null;
}

// ---------- search ----------
function search(q) {
  const nq = norm(q);
  if (!nq) return [];
  const out = [];
  for (const item of state.searchIdx) {
    let best = 0;
    for (const k of item.keys) {
      if (k === nq) best = Math.max(best, 100);
      else if (k.startsWith(nq)) best = Math.max(best, 80 - (k.length - nq.length));
      else if (k.includes(nq)) best = Math.max(best, 50 - (k.length - nq.length));
    }
    if (best > 0) out.push({ ...item, score: best + item.y / 1000 });
  }
  return out.sort((a, b) => b.score - a.score).slice(0, 8);
}

function setupSearch() {
  const input = $("#q"), list = $("#suggest");
  let items = [], active = -1;
  const close = () => { list.hidden = true; input.setAttribute("aria-expanded", "false"); active = -1; };
  const render = () => {
    items = search(input.value);
    if (!items.length) return close();
    list.innerHTML = items.map((it, i) =>
      `<li role="option" id="opt-${i}" data-id="${it.id}" aria-selected="${i === active}">
        <span>${esc(it.label)}</span><small>${esc(it.fam)} · ${it.y}</small></li>`).join("");
    list.hidden = false;
    input.setAttribute("aria-expanded", "true");
    input.setAttribute("aria-activedescendant", active >= 0 ? `opt-${active}` : "");
  };
  const choose = (id) => {
    close();
    input.value = "";
    input.blur();
    const mode = currentMode();
    location.hash = mode === "stock" ? `#/stock/${id}` : mode === "grid" ? `#/grid/${state.dev.get(id).f}` : `#/phone/${id}`;
  };
  input.addEventListener("input", () => { active = -1; render(); });
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") { active = Math.min(active + 1, items.length - 1); render(); e.preventDefault(); }
    else if (e.key === "ArrowUp") { active = Math.max(active - 1, 0); render(); e.preventDefault(); }
    else if (e.key === "Enter" && items.length) { choose(items[Math.max(active, 0)].id); e.preventDefault(); }
    else if (e.key === "Escape") close();
  });
  list.addEventListener("pointerdown", (e) => {
    const li = e.target.closest("li");
    if (li) { e.preventDefault(); choose(li.dataset.id); }
  });
  input.addEventListener("blur", () => setTimeout(close, 120));
}

// ---------- views ----------
function currentMode() {
  const h = location.hash;
  return h.startsWith("#/stock") ? "stock" : h.startsWith("#/grid") ? "grid" : "phone";
}

function cardHTML(edge, sideId, sideLabel) {
  const s = scoreFor(edge);
  if (sideId === "universal") sideLabel = "";
  const cav = s.cv.filter((c) => c !== "other").map((c) => `<span class="chip">${esc(CAVEATS[c]?.[state.lang === "fr" ? 0 : 1] || c)}</span>`).join("");
  const note = topNote(edge);
  const brands = new Set(edge.e.map(([i]) => state.data.ev[i].b));
  const badges = ["axs", "tuff8"].filter((b) => brands.has(b))
    .map((b) => `<span class="badge b-${b}">${b === "axs" ? "AXS" : "TUFF8"}</span>`).join("");
  return `<li><button class="card v-${s.v}" type="button" data-edge="${edge.f}|${edge.u}|${edge.c}">
    <span class="vic" aria-hidden="true">${VERDICT_ICON[s.v]}</span>
    <span class="cbody">
      <span class="cline"><small>${esc(sideLabel)}</small> <strong>${esc(devName(sideId))}</strong> ${badges}</span>
      <span class="cmeta"><span class="vtxt">${esc(t("v")[s.v])}</span> · <span class="k-${s.k}">${esc(t("k")[s.k])}</span> · ${esc(t("reports")(s.n))}</span>
      ${cav ? `<span class="chips">${cav}</span>` : ""}
      ${note ? `<span class="note">${esc(note)}</span>` : ""}
    </span>
    <span class="chev" aria-hidden="true">›</span>
  </button></li>`;
}

function topNote(edge) {
  for (const [i] of edge.e) {
    const ev = state.data.ev[i];
    const n = state.lang === "fr" ? ev.nf || ev.ne : ev.ne || ev.nf;
    if (n && (state.brand === "all" || state.fallback || ev.b === state.brand)) return n;
  }
  return "";
}

function sortEdges(list) {
  return list.sort((a, b) => {
    const sa = scoreFor(a), sb = scoreFor(b);
    return VRANK[sa.v] - VRANK[sb.v] || KRANK[sa.k] - KRANK[sb.k] || sb.n - sa.n;
  });
}

function deviceView(id, mode) {
  const d = state.dev.get(id);
  if (!d) return homeView();
  const all = (mode === "stock" ? state.byFor.get(id) : state.byUsedOn.get(id)) || [];
  state.fallback = false;
  let visible = all.filter(scoreFor);
  if (!visible.length && state.brand !== "all" && all.length) {
    // No brand-specific reports: fall back to all-brand evidence, clearly labelled.
    state.fallback = true;
    visible = all.filter(scoreFor);
  }
  const byCat = new Map();
  for (const e of visible) push(byCat, e.c, e);
  const params = new URLSearchParams(location.hash.split("?")[1] || "");
  const cats = [...byCat.keys()].sort((a, b) => Object.keys(CATS).indexOf(a) - Object.keys(CATS).indexOf(b));
  const sel = cats.includes(params.get("cat")) ? params.get("cat") : "";
  const heading = mode === "stock"
    ? `${t("fitsOthers")} <strong>${esc(d.n)}</strong> ${t("goesOn")}`
    : `${t("fitsThis")} <strong>${esc(d.n)}</strong>`;
  let body = "";
  if (!visible.length) {
    const brandName = state.brand === "axs" ? "AXS" : "TUFF8";
    body = `<div class="empty"><p>${state.brand !== "all" && all.length ? esc(t("noneBrand")(brandName)) + `<button class="link" data-brand-set="all">${t("showAll")}</button>` : esc(t("none"))}</p>
      <p class="muted">${esc(t("noneHint"))}</p></div>`;
  } else {
    const shown = sel ? [sel] : cats;
    body = shown.map((c) => {
      const edges = sortEdges(byCat.get(c));
      const regular = edges.filter((e) => e.f !== "universal");
      const universal = edges.filter((e) => e.f === "universal");
      const side = mode === "stock" ? "u" : "f";
      const label = mode === "stock" ? t("worksOn") : t("madeFor");
      return `<section class="cat"><h3>${esc(catLabel(c))} <small>${edges.length}</small></h3>
        <ul class="cards">${regular.map((e) => cardHTML(e, e[side], label)).join("")}</ul>
        ${universal.length ? `<h4>${esc(t("universal"))}</h4><ul class="cards">${universal.map((e) => cardHTML(e, e.u === id ? e.f : e.u, label)).join("")}</ul>` : ""}
      </section>`;
    }).join("");
  }
  const tabs = cats.length > 1 ? `<div class="tabs" role="tablist">
      <a role="tab" aria-selected="${!sel}" href="#/${mode}/${id}">${t("all")} <small>${visible.length}</small></a>
      ${cats.map((c) => `<a role="tab" aria-selected="${sel === c}" href="#/${mode}/${id}?cat=${c}">${esc(catLabel(c))} <small>${byCat.get(c).length}</small></a>`).join("")}
    </div>` : "";
  const brandName = state.brand === "axs" ? "AXS" : "TUFF8";
  const banner = state.fallback ? `<p class="banner" role="note">${esc(t("fallback")(brandName))}</p>` : "";
  return `<div class="dev-head"><p class="eyebrow">${esc(d.b)} · ${esc(d.f)} · ${d.y}</p><h1>${heading}</h1></div>
    ${banner}${tabs}${body}
    <button class="report" type="button" data-report="${id}">+ ${esc(t("report"))}</button>`;
}

function homeView() {
  const mode = currentMode();
  const pop = POPULAR.filter((id) => state.dev.has(id)).map((id) => {
    const n = (state.byUsedOn.get(id) || []).filter(scoreFor).length;
    return `<a class="pill" href="#/${mode === "stock" ? "stock" : "phone"}/${id}">${esc(state.dev.get(id).n)}${n ? ` <small>${n}</small>` : ""}</a>`;
  }).join("");
  return `<div class="hero"><h1>${esc(t("homeTitle"))}</h1><p>${esc(t("homeSub"))}</p></div>
    <h2 class="sub">${esc(t("popular"))}</h2><div class="pills">${pop}</div>`;
}

function gridView(family) {
  const fams = [...new Set(state.data.devices.map((d) => d.f))];
  family = fams.includes(family) ? family : fams[0];
  const params = new URLSearchParams(location.hash.split("?")[1] || "");
  const cat = CATS[params.get("cat")] ? params.get("cat") : "screen_protector";
  const devs = state.data.devices.filter((d) => d.f === family).sort((a, b) => a.y - b.y || a.n.localeCompare(b.n));
  const ids = new Set(devs.map((d) => d.id));
  const cell = new Map();
  for (const e of state.data.edges) {
    if (e.c === cat && ids.has(e.f) && ids.has(e.u) && scoreFor(e)) cell.set(`${e.f}|${e.u}`, e);
  }
  const short = (n) => n.replace(/^(Galaxy|iPhone|moto|motorola|TCL)\s/i, "").replace(/ \/ .*/, "");
  const head = devs.map((d) => `<th scope="col"><span>${esc(short(d.n))}</span></th>`).join("");
  const rows = devs.map((r) => `<tr><th scope="row">${esc(short(r.n))}</th>${devs.map((c) => {
    if (r.id === c.id) return `<td class="self" aria-label="—"></td>`;
    const e = cell.get(`${r.id}|${c.id}`);
    if (!e) return `<td></td>`;
    const s = scoreFor(e);
    return `<td><button class="cell v-${s.v} k-${s.k}" data-edge="${e.f}|${e.u}|${e.c}" aria-label="${esc(`${r.n} → ${c.n}: ${t("v")[s.v]}`)}">${VERDICT_ICON[s.v]}</button></td>`;
  }).join("")}</tr>`).join("");
  return `<div class="grid-ctl">
      <label>${esc(t("family"))} <select id="g-fam">${fams.map((f) => `<option ${f === family ? "selected" : ""}>${esc(f)}</option>`).join("")}</select></label>
      <label>${esc(t("category"))} <select id="g-cat">${Object.keys(CATS).map((c) => `<option value="${c}" ${c === cat ? "selected" : ""}>${esc(catLabel(c))}</option>`).join("")}</select></label>
    </div>
    ${state.fallback ? `<p class="banner" role="note">${esc(t("fallback")(state.brand === "axs" ? "AXS" : "TUFF8"))}</p>` : ""}
    <p class="muted">${esc(t("gridHint"))}</p>
    <div class="grid-wrap"><table class="grid"><thead><tr><th></th>${head}</tr></thead><tbody>${rows}</tbody></table></div>`;
}

// ---------- evidence sheet ----------
function openEdge(key) {
  const [f, u, c] = key.split("|");
  const edge = state.data.edges.find((e) => e.f === f && e.u === u && e.c === c);
  if (!edge) return;
  const s = scoreFor(edge) || edge.s.all;
  $("#sheet-title").textContent = `${devName(f)} → ${devName(u)}`;
  const items = edge.e
    .filter(([i]) => state.brand === "all" || state.fallback || state.data.ev[i].b === state.brand)
    .map(([i, v, k]) => {
      const ev = state.data.ev[i];
      const vv = { y: "fits", c: "fits_with_caveat", n: "doesnt_fit" }[v];
      const note = state.lang === "fr" ? ev.nf || ev.ne : ev.ne || ev.nf;
      return `<li class="ev v-${vv}">
        <p class="ev-top"><span class="vic sm" aria-hidden="true">${VERDICT_ICON[vv]}</span> <strong>${esc(t("v")[vv])}</strong>
          · ${esc(t("src")[ev.s] || ev.s)} · ${esc(ev.d)} · ${esc(k === "f" ? t("firsthand") : t("secondhand"))}
          ${ev.br ? ` · <span class="badge ${ev.b !== "other" ? "b-" + ev.b : ""}">${esc(ev.br)}</span>` : ""}</p>
        <blockquote>“${esc(ev.q)}”</blockquote>
        ${note ? `<p class="note">${esc(note)}</p>` : ""}
        <p class="ev-src"><small>${esc(ev.x)}</small> <a href="${esc(ev.u)}" target="_blank" rel="noopener noreferrer">${esc(t("open"))} ↗</a></p>
      </li>`;
    }).join("");
  $("#sheet-body").innerHTML = `<p class="sheet-sum v-${s.v}"><span class="vic" aria-hidden="true">${VERDICT_ICON[s.v]}</span>
      <span><strong>${esc(catLabel(c))}: ${esc(t("v")[s.v])}</strong><br>${esc(t("k")[s.k])} · ${esc(t("reports")(s.n))}</span></p>
    <h3>${esc(t("sources"))}</h3><ul class="evs">${items}</ul>`;
  $("#sheet").showModal();
}

function openReport(id) {
  const opts = state.data.devices.map((d) => `<option value="${d.id}" ${d.id === id ? "selected" : ""}>${esc(d.n)}</option>`).join("");
  $("#sheet-title").textContent = t("reportTitle");
  $("#sheet-body").innerHTML = `<p class="muted">${esc(t("reportIntro"))}</p>
    <form id="rep" class="rep">
      <label>${esc(t("category"))}<select name="c">${Object.keys(CATS).map((c) => `<option value="${c}">${esc(catLabel(c))}</option>`).join("")}</select></label>
      <label>${esc(t("accFor"))}<select name="f">${opts}</select></label>
      <label>${esc(t("putOn"))}<select name="u">${opts}</select></label>
      <fieldset><legend>${esc(t("result"))}</legend>
        ${["fits", "fits_with_caveat", "doesnt_fit"].map((v, i) => `<label class="radio"><input type="radio" name="v" value="${v}" ${i ? "" : "checked"}> ${esc(t("v")[v])}</label>`).join("")}
      </fieldset>
      <label>${esc(t("brandLbl"))}<input name="b" autocomplete="off"></label>
      <label>${esc(t("notes"))}<textarea name="n" rows="2"></textarea></label>
      <div class="rep-actions"><button type="submit" data-act="share">${esc(t("share"))}</button><button type="submit" data-act="copy" class="ghost">${esc(t("copy"))}</button></div>
    </form>`;
  $("#rep").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const rec = { accessory_for: fd.get("f"), used_on: fd.get("u"), category: fd.get("c"), verdict: fd.get("v"),
      brand: fd.get("b") || "unknown", notes: fd.get("n"), date: new Date().toISOString().slice(0, 10) };
    const text = `FitMap: ${catLabel(rec.category)} — ${devName(rec.accessory_for)} → ${devName(rec.used_on)}: ${t("v")[rec.verdict]}` +
      `${rec.brand !== "unknown" ? ` (${rec.brand})` : ""}${rec.notes ? `. ${rec.notes}` : ""}\n${JSON.stringify(rec)}`;
    if (e.submitter?.dataset.act === "share" && navigator.share) {
      try { await navigator.share({ text }); return; } catch { /* cancelled: fall through to copy */ }
    }
    await navigator.clipboard.writeText(text).catch(() => {});
    e.submitter.textContent = t("copied");
  });
  $("#sheet").showModal();
}

// ---------- shell ----------
function applyI18n() {
  document.documentElement.lang = state.lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
  $("#lang").textContent = state.lang === "fr" ? "EN" : "FR";
  $("#lang").setAttribute("aria-label", state.lang === "fr" ? "EN (English)" : "FR (français)");
  $("#q").placeholder = currentMode() === "stock" ? t("phStock") : t("phPhone");
  $("#q").setAttribute("aria-label", $("#q").placeholder);
  if (state.data) $("#meta").textContent = t("updated")(state.data.generated, state.data.stats.sources);
}

function applyBrand() {
  document.querySelectorAll("#brands [data-brand]").forEach((b) =>
    b.setAttribute("aria-checked", String(b.dataset.brand === state.brand)));
}

function route() {
  const [path] = location.hash.replace(/^#/, "").split("?");
  const parts = path.split("/").filter(Boolean);
  const mode = currentMode();
  document.querySelectorAll(".modes a").forEach((a) => a.setAttribute("aria-current", String(a.dataset.mode === mode)));
  applyI18n();
  // Home and grid: if the selected brand has no reports anywhere, show all-brand data.
  state.fallback = state.brand !== "all" && !state.data.edges.some((e) => e.s[state.brand]);
  let html;
  if (mode === "grid") html = gridView(decodeURIComponent(parts[1] || ""));
  else if (parts[1] && state.dev.has(parts[1])) html = deviceView(parts[1], mode);
  else html = homeView();
  $("#main").innerHTML = html;
  const fam = $("#g-fam"), cat = $("#g-cat");
  if (fam) {
    const go = () => { location.hash = `#/grid/${encodeURIComponent(fam.value)}?cat=${cat.value}`; };
    fam.addEventListener("change", go);
    cat.addEventListener("change", go);
  }
}

function events() {
  document.addEventListener("click", (e) => {
    const card = e.target.closest("[data-edge]");
    if (card) return openEdge(card.dataset.edge);
    const rep = e.target.closest("[data-report]");
    if (rep) return openReport(rep.dataset.report);
    const bset = e.target.closest("[data-brand-set]");
    const b = e.target.closest("#brands [data-brand]") || bset;
    if (b) {
      state.brand = b.dataset.brand || b.dataset.brandSet;
      localStorage.setItem("brand", state.brand);
      applyBrand();
      route();
      return;
    }
    if (e.target.closest("[data-close]") || e.target === $("#sheet")) $("#sheet").close();
  });
  $("#lang").addEventListener("click", () => {
    state.lang = state.lang === "fr" ? "en" : "fr";
    localStorage.setItem("lang", state.lang);
    route();
  });
  window.addEventListener("hashchange", () => { route(); $("#main").focus({ preventScroll: true }); window.scrollTo(0, 0); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== $("#q") && !$("#sheet").open) { e.preventDefault(); $("#q").focus(); }
  });
}

(async function init() {
  applyBrand();
  applyI18n();
  events();
  setupSearch();
  await load();
  route();
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
})();
