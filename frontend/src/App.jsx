import { useEffect, useState } from "react";
import { uploadFile, loadSample, getDocuments, getTimeline, getPatient, saveAbha, fhirUrl } from "./api";

const SAMPLES = [
  ["cbc_sample", { en: "Blood count report", ta: "இரத்த பரிசோதனை" }],
  ["lipid_sample", { en: "Lipid + thyroid report", ta: "கொழுப்பு + தைராய்டு" }],
  ["prescription_sample", { en: "Prescription", ta: "மருந்துச் சீட்டு" }],
  ["discharge_sample", { en: "Discharge summary", ta: "டிஸ்சார்ஜ் சுருக்கம்" }],
];

const T = {
  en: {
    appName: "Health Copilot", byLab: "by Altrixs Lab", tagline: "Understand your medical records in plain language",
    upload: "Upload", timeline: "Timeline",
    drop: "Drag a report here, or click to choose (PDF, JPG, PNG)",
    trySamples: "Or try a sample report", processing: "Reading your document... this can take up to 30 seconds",
    summary: "Plain-language summary", questions: "Questions to ask your doctor",
    labs: "Lab results", medicines: "Medicines listed", conditions: "Conditions mentioned",
    test: "Test", value: "Value", range: "Reference range", status: "Status", source: "Source line",
    drug: "Medicine", dose: "Dose", freq: "How often", duration: "For how long",
    verify: "Please verify", yourRecords: "Your records", empty: "No records yet. Upload a report to begin.",
    all: "All", labsF: "Labs", medsF: "Medicines", condF: "Conditions",
    fhir: "Download FHIR JSON", abha: "ABHA ID (mock)", save: "Save",
    disclaimer: "Not medical advice. Please consult your doctor.",
    flags: { low: "Low", high: "High", normal: "Normal", unknown: "No range" },
    noTamil: "Tamil summary is not available for this record.",
    emergencyLead: "EMERGENCY:", emergencyText: "Chest pain, severe breathlessness, or heavy bleeding? Call 108 immediately.",
    call108: "CALL 108 NOW", nearbyER: "Nearby ER",
    a11yHint: "Elderly-friendly readable fonts & accessible controls",
    contrast: "Contrast", lowData: "Low Data", theme: "Switch theme",
    records: "Records", recordsSub: "Uploaded", attention: "Needs attention", attentionSub: "High or low results",
    toVerify: "To verify", toVerifySub: "Check with source",
  },
  ta: {
    appName: "ஹெல்த் கோபைலட்", byLab: "ஆல்ட்ரிக்ஸ் லேப்", tagline: "உங்கள் மருத்துவ அறிக்கைகளை எளிய மொழியில் புரிந்துகொள்ளுங்கள்",
    upload: "பதிவேற்று", timeline: "காலவரிசை",
    drop: "அறிக்கையை இங்கே இழுத்து விடவும் அல்லது தேர்ந்தெடுக்கவும் (PDF, JPG, PNG)",
    trySamples: "அல்லது மாதிரி அறிக்கையை முயற்சிக்கவும்", processing: "அறிக்கையைப் படிக்கிறது... 30 வினாடிகள் வரை ஆகலாம்",
    summary: "எளிய விளக்கம்", questions: "மருத்துவரிடம் கேட்க வேண்டிய கேள்விகள்",
    labs: "பரிசோதனை முடிவுகள்", medicines: "பட்டியலிடப்பட்ட மருந்துகள்", conditions: "குறிப்பிடப்பட்ட நிலைகள்",
    test: "பரிசோதனை", value: "மதிப்பு", range: "சாதாரண வரம்பு", status: "நிலை", source: "மூல வரி",
    drug: "மருந்து", dose: "அளவு", freq: "எத்தனை முறை", duration: "எத்தனை நாட்கள்",
    verify: "சரிபார்க்கவும்", yourRecords: "உங்கள் பதிவுகள்", empty: "இன்னும் பதிவுகள் இல்லை. ஒரு அறிக்கையைப் பதிவேற்றவும்.",
    all: "அனைத்தும்", labsF: "பரிசோதனைகள்", medsF: "மருந்துகள்", condF: "நிலைகள்",
    fhir: "FHIR JSON பதிவிறக்கம்", abha: "ABHA எண் (மாதிரி)", save: "சேமி",
    disclaimer: "இது மருத்துவ ஆலோசனை அல்ல. தயவுசெய்து உங்கள் மருத்துவரை அணுகவும்.",
    flags: { low: "குறைவு", high: "அதிகம்", normal: "சாதாரணம்", unknown: "வரம்பு இல்லை" },
    noTamil: "இந்தப் பதிவுக்கு தமிழ் சுருக்கம் கிடைக்கவில்லை.",
    emergencyLead: "அவசரம்:", emergencyText: "நெஞ்சு வலி, கடுமையான மூச்சுத் திணறல் அல்லது அதிக ரத்தப்போக்கா? உடனே 108-ஐ அழைக்கவும்.",
    call108: "இப்போதே 108 அழை", nearbyER: "அருகிலுள்ள ER",
    a11yHint: "முதியோர்களுக்கான பெரிய எழுத்து & உயர் மாறுபாடு வசதி",
    contrast: "உயர் மாறுபாடு", lowData: "குறைந்த தரவு", theme: "தீம் மாற்று",
    records: "பதிவுகள்", recordsSub: "பதிவேற்றியவை", attention: "கவனம் தேவை", attentionSub: "அதிகம் அல்லது குறைவு",
    toVerify: "சரிபார்க்க", toVerifySub: "மூலத்துடன் ஒப்பிடுக",
  },
};

/* ---------- Icons ---------- */
const Svg = ({ children, size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{children}</svg>
);
const IconPulse = () => <Svg size={24}><path d="M3 12h4l2-6 4 12 2-6h6" /></Svg>;
const IconAlert = () => <Svg size={18}><path d="M12 3l10 18H2L12 3z" /><path d="M12 10v4M12 18h.01" /></Svg>;
const IconPhone = () => <Svg size={14}><path d="M5 3h4l2 5-2.5 1.5a11 11 0 006 6L16 13l5 2v4a2 2 0 01-2 2A16 16 0 013 5a2 2 0 012-2z" /></Svg>;
const IconPin = () => <Svg size={14}><path d="M12 21s-7-6-7-11a7 7 0 0114 0c0 5-7 11-7 11z" /><circle cx="12" cy="10" r="2.5" /></Svg>;
const IconTranslate = () => <Svg size={16}><path d="M4 5h9M8.5 3v2M6 5c1 4 3.5 7 7 9M12 5c-1 4-3.5 7-7 9" /><path d="M13 21l4-10 4 10M14.5 18h5" /></Svg>;
const IconType = () => <Svg size={15}><path d="M5 6V4h14v2M12 4v16M9 20h6" /></Svg>;
const IconEye = () => <Svg size={15}><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z" /><circle cx="12" cy="12" r="3" /></Svg>;
const IconZap = () => <Svg size={15}><path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z" /></Svg>;
const IconMoon = () => <Svg size={16}><path d="M20 14.5A8 8 0 019.5 4a8 8 0 1010.5 10.5z" /></Svg>;
const IconSun = () => <Svg size={16}><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></Svg>;
const IconUpload = () => <Svg size={28}><path d="M12 16V4M7 9l5-5 5 5" /><path d="M4 16v3a1 1 0 001 1h14a1 1 0 001-1v-3" /></Svg>;
const IconUp = () => <Svg size={16}><path d="M12 19V5M6 11l6-6 6 6" /></Svg>;
const IconClock = () => <Svg size={16}><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></Svg>;
const IconDownload = () => <Svg size={16}><path d="M12 4v12M7 11l5 5 5-5" /><path d="M4 20h16" /></Svg>;
const IconLab = () => <Svg size={20}><path d="M9 3h6M10 3v6l-5 9a2 2 0 001.8 3h10.4A2 2 0 0019 18l-5-9V3" /></Svg>;
const IconPill = () => <Svg size={20}><rect x="3" y="9" width="18" height="6" rx="3" transform="rotate(-35 12 12)" /><path d="M9.5 8.5l6 6" /></Svg>;
const IconHeart = () => <Svg size={20}><path d="M12 20s-7-4.4-7-10a4 4 0 017-2.5A4 4 0 0119 10c0 5.6-7 10-7 10z" /></Svg>;
const IconNote = () => <Svg size={20}><path d="M6 3h9l4 4v14H6z" /><path d="M9 12h7M9 16h7" /></Svg>;
const IconSpark = () => <Svg size={15}><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z" /></Svg>;

/* ---------- Small components ---------- */
function Badge({ flag, label }) {
  return <span className={"badge " + flag}>{label}</span>;
}

// Shows where a lab value sits against its reference range.
function Gauge({ value, low, high, flag, rangeText }) {
  const v = Number(value), lo = Number(low), hi = Number(high);
  const ok = value !== null && low !== null && high !== null && [v, lo, hi].every(Number.isFinite) && hi > lo;
  if (!ok) return <div className="gauge-range">{rangeText}</div>;
  const span = hi - lo;
  const start = lo - span * 0.5;
  const pos = Math.min(0.97, Math.max(0.03, (v - start) / (span * 2)));
  return (
    <div className="gauge">
      <div className="gauge-track">
        <div className="gauge-zone" />
        <div className={"gauge-dot " + flag} style={{ left: pos * 100 + "%" }} />
      </div>
      <div className="gauge-range">{rangeText}</div>
    </div>
  );
}

function DocView({ doc, lang, t }) {
  const s = doc.summary;
  const text = lang === "ta" ? s.ta : s.en;
  const questions = (s.questions_for_doctor && s.questions_for_doctor[lang]) || [];
  const meds = doc.medications, conds = doc.conditions, obs = doc.observations;

  const count = (f) => obs.filter((o) => o.flag === f).length;
  const reviewCount = obs.filter((o) => o.needs_review).length;

  return (
    <div>
      <div className="card">
        <div className="doc-meta">
          <span className="file">{doc.filename}</span>
          {doc.doc_date && <span>{doc.doc_date}</span>}
        </div>
        <h2><span className="h-icon"><IconNote /></span>{t.summary}</h2>
        <p className="summary">{text || t.noTamil}</p>
        {questions.length > 0 && (
          <>
            <h3>{t.questions}</h3>
            <ul className="questions">{questions.map((q, i) => <li key={i}>{q}</li>)}</ul>
          </>
        )}
        <p className="disclaimer">{t.disclaimer}</p>
      </div>

      {obs.length > 0 && (
        <div className="card">
          <h2><span className="h-icon"><IconLab /></span>{t.labs}</h2>
          <div className="stats">
            {count("high") > 0 && <span className="stat high"><b>{count("high")}</b>{t.flags.high}</span>}
            {count("low") > 0 && <span className="stat low"><b>{count("low")}</b>{t.flags.low}</span>}
            {count("normal") > 0 && <span className="stat normal"><b>{count("normal")}</b>{t.flags.normal}</span>}
            {reviewCount > 0 && <span className="stat review"><b>{reviewCount}</b>{t.verify}</span>}
          </div>
          <div className="scroll">
            <table>
              <thead>
                <tr><th>{t.test}</th><th>{t.value}</th><th>{t.range}</th><th>{t.status}</th><th>{t.source}</th></tr>
              </thead>
              <tbody>
                {obs.map((o) => (
                  <tr key={o.id}>
                    <td className="test">{o.test}</td>
                    <td className="value">{o.value === null ? "?" : `${o.value} ${o.unit}`}</td>
                    <td>
                      <Gauge value={o.value} low={o.ref_low} high={o.ref_high} flag={o.flag}
                        rangeText={`${o.ref_low ?? "–"} to ${o.ref_high ?? "–"}`} />
                    </td>
                    <td>
                      <div className="badge-stack">
                        <Badge flag={o.flag} label={t.flags[o.flag]} />
                        {o.needs_review && <span className="badge review">{t.verify}</span>}
                      </div>
                    </td>
                    <td className="muted small">{o.source_text}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {meds.length > 0 && (
        <div className="card">
          <h2><span className="h-icon"><IconPill /></span>{t.medicines}</h2>
          <div className="scroll">
            <table>
              <thead>
                <tr><th>{t.drug}</th><th>{t.dose}</th><th>{t.freq}</th><th>{t.duration}</th><th>{t.source}</th></tr>
              </thead>
              <tbody>
                {meds.map((m) => (
                  <tr key={m.id}>
                    <td className="test">{m.drug}{m.needs_review && <span className="badge review">{t.verify}</span>}</td>
                    <td>{m.dose}</td><td>{m.frequency}</td><td>{m.duration}</td>
                    <td className="muted small">{m.source_text}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {conds.length > 0 && (
        <div className="card">
          <h2><span className="h-icon"><IconHeart /></span>{t.conditions}</h2>
          <ul className="cond-list">{conds.map((c) => <li key={c.id}>{c.name}</li>)}</ul>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [lang, setLang] = useState("en");
  const [tab, setTab] = useState("upload");
  const [abha, setAbha] = useState("");
  const [docs, setDocs] = useState([]);
  const [events, setEvents] = useState([]);
  const [current, setCurrent] = useState(null);
  const [filter, setFilter] = useState("all");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [drag, setDrag] = useState(false);
  const [fontSize, setFontSize] = useState("base");
  const [contrast, setContrast] = useState(false);
  const [lowData, setLowData] = useState(false);
  const [dark, setDark] = useState(false);
  const t = T[lang];

  // Accessibility settings are applied to the page itself.
  useEffect(() => {
    document.documentElement.style.fontSize = { sm: "90%", base: "100%", lg: "115%" }[fontSize];
  }, [fontSize]);
  useEffect(() => { document.body.classList.toggle("high-contrast", contrast); }, [contrast]);
  useEffect(() => { document.body.classList.toggle("low-data", lowData); }, [lowData]);
  useEffect(() => { document.documentElement.dataset.theme = dark ? "dark" : "light"; }, [dark]);
  useEffect(() => { document.documentElement.lang = lang === "ta" ? "ta" : "en"; }, [lang]);

  async function refresh() {
    try {
      const [d, tl] = await Promise.all([getDocuments(), getTimeline()]);
      setDocs(d);
      setEvents(tl.events);
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    getPatient().then((p) => setAbha(p.abha_id)).catch((e) => setError(e.message));
    refresh();
  }, []);

  async function run(action) {
    setError("");
    setBusy(true);
    try {
      const doc = await action();
      setCurrent(doc);
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  const onFile = (file) => file && run(() => uploadFile(file));

  async function onSaveAbha() {
    try {
      const p = await saveAbha(abha);
      setAbha(p.abha_id);
      setError("");
    } catch (e) {
      setError(e.message);
    }
  }

  const shownEvents = events.filter((e) => filter === "all" || e.type === filter);
  const filters = [["all", t.all], ["lab", t.labsF], ["medication", t.medsF], ["condition", t.condF]];

  const allObs = docs.flatMap((d) => d.observations || []);
  const attention = allObs.filter((o) => o.flag === "high" || o.flag === "low").length;
  const toVerify = allObs.filter((o) => o.needs_review).length
    + docs.flatMap((d) => d.medications || []).filter((m) => m.needs_review).length;

  return (
    <>
      <div className="emergency">
        <div className="emergency-inner">
          <div className="emergency-msg">
            <span className="pulse-dot" /><IconAlert />
            <span><b>{t.emergencyLead}</b> {t.emergencyText}</span>
          </div>
          <div className="emergency-actions">
            <a className="pill-btn white" href="tel:108"><IconPhone />{t.call108}</a>
            <a className="pill-btn dark" target="_blank" rel="noreferrer"
              href="https://www.google.com/maps/search/emergency+hospital+near+me"><IconPin />{t.nearbyER}</a>
          </div>
        </div>
      </div>

      <div className="a11y">
        <div className="a11y-inner">
          <div className="a11y-left">
            <div className="group">
              <span className="g-icon"><IconTranslate /></span>
              <button className={lang === "ta" ? "on solid" : ""} onClick={() => setLang("ta")}>தமிழ்</button>
              <button className={lang === "en" ? "on solid" : ""} onClick={() => setLang("en")}>English</button>
            </div>
            <span className="a11y-hint">{t.a11yHint}</span>
          </div>
          <div className="a11y-right">
            <div className="group" role="group" aria-label="Text size">
              <span className="g-icon"><IconType /></span>
              <button className={fontSize === "sm" ? "on" : ""} onClick={() => setFontSize("sm")} aria-label="Smaller text">A-</button>
              <button className={fontSize === "base" ? "on" : ""} onClick={() => setFontSize("base")} aria-label="Normal text">A</button>
              <button className={fontSize === "lg" ? "on" : ""} onClick={() => setFontSize("lg")} aria-label="Larger text">A+</button>
            </div>
            <button className={"btn-ghost" + (contrast ? " on" : "")} onClick={() => setContrast(!contrast)} aria-pressed={contrast}>
              <IconEye />{t.contrast}
            </button>
            <button className={"btn-ghost" + (lowData ? " on" : "")} onClick={() => setLowData(!lowData)} aria-pressed={lowData}>
              <IconZap />{t.lowData}
            </button>
            <button className="btn-ghost" onClick={() => setDark(!dark)} aria-label={t.theme} title={t.theme}>
              {dark ? <IconSun /> : <IconMoon />}
            </button>
          </div>
        </div>
      </div>

      <header className="topbar">
        <div className="topbar-inner">
          <div className="logo">
            <div className="logo-mark"><IconPulse /></div>
            <div className="logo-text">
              <b>{t.appName}</b>
              <span>{lang === "en" ? "by " : ""}<em>{t.byLab}</em></span>
            </div>
          </div>
          <nav className="nav">
            <button className={tab === "upload" ? "on" : ""} onClick={() => setTab("upload")}><IconUp />{t.upload}</button>
            <button className={tab === "timeline" ? "on" : ""} onClick={() => setTab("timeline")}><IconClock />{t.timeline}</button>
          </nav>
          <div className="topbar-right">
            <a className="fhir" href={fhirUrl()} target="_blank" rel="noreferrer"><IconDownload />{t.fhir}</a>
          </div>
        </div>
      </header>

      <main className="page">
        <section className="banner">
          <div className="banner-main">
            <span className="pill"><IconSpark />{t.appName}</span>
            <h2>{t.tagline}</h2>
            <div className="abha">
              <label htmlFor="abha-input">{t.abha}</label>
              <div className="row">
                <input id="abha-input" value={abha} onChange={(e) => setAbha(e.target.value)} />
                <button className="small-btn" onClick={onSaveAbha}>{t.save}</button>
              </div>
            </div>
          </div>
          <div className="tiles">
            <div className="tile"><div className="tile-label">{t.records}</div><b>{docs.length}</b><div className="tile-sub">{t.recordsSub}</div></div>
            <div className="tile"><div className="tile-label">{t.attention}</div><b>{attention}</b><div className="tile-sub">{t.attentionSub}</div></div>
            <div className="tile"><div className="tile-label">{t.toVerify}</div><b>{toVerify}</b><div className="tile-sub">{t.toVerifySub}</div></div>
          </div>
        </section>

        {error && <div className="error" role="alert">{error}</div>}

        {tab === "upload" && (
          <>
            <label
              className={"drop" + (drag ? " drag" : "")}
              onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
              onDragLeave={() => setDrag(false)}
              onDrop={(e) => { e.preventDefault(); setDrag(false); onFile(e.dataTransfer.files[0]); }}
            >
              <input type="file" accept=".pdf,.jpg,.jpeg,.png" hidden
                onChange={(e) => { onFile(e.target.files[0]); e.target.value = ""; }} />
              <span className="drop-icon"><IconUpload /></span>
              <span className="drop-text">{t.drop}</span>
            </label>

            <div className="samples">
              <span className="muted">{t.trySamples}:</span>
              {SAMPLES.map(([name, label]) => (
                <button key={name} className="chip" disabled={busy} onClick={() => run(() => loadSample(name))}>
                  {label[lang]}
                </button>
              ))}
            </div>

            {busy && <div className="loading" role="status"><span className="spinner" />{t.processing}</div>}

            {docs.length > 0 && (
              <div className="samples">
                <span className="muted">{t.yourRecords}:</span>
                {docs.map((d) => (
                  <button key={d.id} className={"chip" + (current && current.id === d.id ? " on" : "")}
                    onClick={() => setCurrent(d)}>
                    {d.filename}
                  </button>
                ))}
              </div>
            )}

            {current ? <DocView doc={current} lang={lang} t={t} /> : !busy && <p className="muted center empty">{t.empty}</p>}
          </>
        )}

        {tab === "timeline" && (
          <div className="card">
            <div className="samples" style={{ marginTop: 0 }}>
              {filters.map(([key, label]) => (
                <button key={key} className={"chip" + (filter === key ? " on" : "")} onClick={() => setFilter(key)}>
                  {label}
                </button>
              ))}
            </div>
            {shownEvents.length === 0 && <p className="muted center empty">{t.empty}</p>}
            <ul className="timeline">
              {shownEvents.map((e, i) => (
                <li key={i}>
                  <div className="date">{e.date}</div>
                  <span className={"dot " + (e.type === "lab" ? e.flag : e.type)} />
                  <div>
                    <div className="title">
                      <strong>{e.title}</strong>
                      {e.type === "lab" && <Badge flag={e.flag} label={t.flags[e.flag]} />}
                    </div>
                    <div className="muted small">{e.detail}</div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </main>

      <footer className="disclaimer">{t.disclaimer}</footer>
    </>
  );
}