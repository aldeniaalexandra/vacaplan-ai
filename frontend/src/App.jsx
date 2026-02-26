import { useState, useEffect, useRef } from "react";

const AGENT_STEPS = [
  { id: "calendar", icon: "📅", label: "Checking your calendar", detail: "Scanning availability in June–July..." },
  { id: "prefs", icon: "🧠", label: "Loading preferences", detail: "Beach lover · Budget: $3,000 · Cuisine: Asian" },
  { id: "flights", icon: "✈️", label: "Searching flights", detail: "BKK, DPS, SGN — 14 routes found" },
  { id: "hotels", icon: "🏨", label: "Finding hotels", detail: "Filtering 4–5 star, ocean view, pet-friendly" },
  { id: "activities", icon: "🎯", label: "Curating activities", detail: "Temples, scuba, night markets, cooking class" },
  { id: "budget", icon: "💰", label: "Optimizing budget", detail: "Total estimate: $2,740 · Savings: $260" },
  { id: "plan", icon: "🗺️", label: "Finalizing itinerary", detail: "7-day Bali trip ready!" },
];

const ITINERARY = [
  { day: 1, title: "Arrival & Seminyak", activities: ["Land at Ngurah Rai Airport", "Check-in: The Layar Villas", "Sunset at Ku De Ta beach bar"], cost: "$320" },
  { day: 2, title: "Ubud & Rice Terraces", activities: ["Tegallalang Rice Terraces sunrise", "Tirta Empul holy spring temple", "Traditional Balinese cooking class"], cost: "$85" },
  { day: 3, title: "Scuba & Nusa Lembongan", activities: ["Ferry to Nusa Lembongan", "Crystal Bay scuba diving (2 dives)", "Devil's Tears sunset cliffs"], cost: "$120" },
  { day: 4, title: "Cultural Immersion", activities: ["Tanah Lot sea temple", "Kecak fire dance at Uluwatu", "Jimbaran seafood BBQ dinner"], cost: "$95" },
  { day: 5, title: "Adventure Day", activities: ["Mount Batur volcano sunrise trek", "Kintamani coffee plantation tour", "Spa & massage afternoon"], cost: "$110" },
  { day: 6, title: "Beach & Market Day", activities: ["Canggu surf lesson", "Seminyak boutique shopping", "Potato Head Beach Club evening"], cost: "$140" },
  { day: 7, title: "Departure", activities: ["Spa morning ritual", "Last beachside breakfast", "Transfer to airport"], cost: "$60" },
];

const FLIGHTS = [
  { from: "Jakarta (CGK)", to: "Bali (DPS)", airline: "Garuda Indonesia", time: "06:30 → 08:45", price: "$89", badge: "Best Value" },
  { from: "Bali (DPS)", to: "Jakarta (CGK)", airline: "Lion Air", time: "18:00 → 20:15", price: "$74", badge: null },
];

const HOTELS = [
  { name: "The Layar Private Villas", location: "Seminyak", stars: 5, price: "$240/night", features: ["Private pool", "Ocean view", "Breakfast incl."] },
  { name: "Alaya Resort Ubud", location: "Ubud", stars: 4, price: "$160/night", features: ["Rice field view", "Spa", "Yoga deck"] },
];

export default function VacaPlanAI() {
  const [screen, setScreen] = useState("home"); // home | preferences | planning | result
  const [stepIndex, setStepIndex] = useState(0);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [prefs, setPrefs] = useState({ destination: "Bali, Indonesia", dates: "Jun 14 – Jun 21, 2025", budget: "$3,000", travelers: "2 adults", style: "Beach & Culture" });
  const [activeDay, setActiveDay] = useState(0);
  const [bookingMode, setBookingMode] = useState(false);
  const [booked, setBooked] = useState(false);
  const [payInfo, setPayInfo] = useState({ name: "Sarah Chen", card: "•••• •••• •••• 4242", expiry: "12/27" });
  const plannerRef = useRef(null);

  useEffect(() => {
    if (screen !== "planning") return;
    if (stepIndex >= AGENT_STEPS.length) {
      setTimeout(() => setScreen("result"), 600);
      return;
    }
    const timer = setTimeout(() => {
      setCompletedSteps(prev => [...prev, AGENT_STEPS[stepIndex].id]);
      setStepIndex(prev => prev + 1);
    }, 900);
    return () => clearTimeout(timer);
  }, [screen, stepIndex]);

  const startPlanning = () => {
    setCompletedSteps([]);
    setStepIndex(0);
    setScreen("planning");
  };

  const totalCost = ITINERARY.reduce((s, d) => s + parseInt(d.cost.replace("$", "")), 0);

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0a0a0f 0%, #0d1a2e 50%, #0a1a12 100%)",
      fontFamily: "'Georgia', 'Times New Roman', serif",
      color: "#e8e4dc",
      position: "relative",
      overflow: "hidden"
    }}>
      {/* Ambient background orbs */}
      <div style={{ position: "fixed", top: "-20%", right: "-10%", width: "600px", height: "600px", borderRadius: "50%", background: "radial-gradient(circle, rgba(14,165,110,0.08) 0%, transparent 70%)", pointerEvents: "none" }} />
      <div style={{ position: "fixed", bottom: "-10%", left: "-10%", width: "500px", height: "500px", borderRadius: "50%", background: "radial-gradient(circle, rgba(59,130,246,0.06) 0%, transparent 70%)", pointerEvents: "none" }} />
      <div style={{ position: "fixed", top: "40%", left: "20%", width: "300px", height: "300px", borderRadius: "50%", background: "radial-gradient(circle, rgba(245,158,11,0.04) 0%, transparent 70%)", pointerEvents: "none" }} />

      <div style={{ maxWidth: "960px", margin: "0 auto", padding: "0 24px" }}>

        {/* ─── NAV ─── */}
        <nav style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "24px 0 16px", borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div style={{ width: "36px", height: "36px", background: "linear-gradient(135deg, #0e9a6e, #3b82f6)", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "18px" }}>🌴</div>
            <span style={{ fontSize: "20px", fontWeight: "700", letterSpacing: "-0.5px", color: "#fff" }}>VacaPlan<span style={{ color: "#0e9a6e" }}>AI</span></span>
          </div>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <span style={{ fontSize: "12px", color: "#6b7a8d", fontFamily: "monospace" }}>Powered by Claude</span>
            <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#0e9a6e", boxShadow: "0 0 8px #0e9a6e" }} />
          </div>
        </nav>

        {/* ─── HOME SCREEN ─── */}
        {screen === "home" && (
          <div style={{ paddingTop: "60px", paddingBottom: "60px" }}>
            <div style={{ textAlign: "center", marginBottom: "64px" }}>
              <div style={{ display: "inline-block", background: "rgba(14,154,110,0.12)", border: "1px solid rgba(14,154,110,0.3)", borderRadius: "100px", padding: "6px 16px", fontSize: "13px", color: "#0e9a6e", marginBottom: "24px", fontFamily: "monospace" }}>
                ✦ Agentic AI Vacation Planner
              </div>
              <h1 style={{ fontSize: "clamp(36px, 6vw, 64px)", fontWeight: "800", lineHeight: "1.1", marginBottom: "20px", letterSpacing: "-2px", color: "#fff" }}>
                Your dream trip,<br />
                <span style={{ background: "linear-gradient(90deg, #0e9a6e, #3b82f6)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>planned autonomously.</span>
              </h1>
              <p style={{ fontSize: "18px", color: "#8899aa", maxWidth: "480px", margin: "0 auto 40px", lineHeight: "1.7" }}>
                Tell us your preferences. Our AI agent checks your calendar, finds the best deals, and books everything — so you just pack your bags.
              </p>

              {/* Capability pills */}
              <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", justifyContent: "center", marginBottom: "48px" }}>
                {["📅 Calendar-aware", "✈️ Flight search", "🏨 Hotel booking", "🎯 Activity curation", "💳 Auto-booking", "🔒 Payment-secured"].map(c => (
                  <span key={c} style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "100px", padding: "8px 16px", fontSize: "13px", color: "#aab" }}>{c}</span>
                ))}
              </div>

              <button onClick={() => setScreen("preferences")} style={{ background: "linear-gradient(135deg, #0e9a6e, #059860)", color: "#fff", border: "none", padding: "16px 44px", borderRadius: "14px", fontSize: "17px", fontWeight: "700", cursor: "pointer", letterSpacing: "-0.3px", boxShadow: "0 8px 32px rgba(14,154,110,0.4)", fontFamily: "inherit" }}>
                Plan My Vacation →
              </button>
            </div>

            {/* Feature cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "16px" }}>
              {[
                { icon: "🤖", title: "Agentic Planning", desc: "Multi-step AI agent autonomously searches flights, hotels, and activities using real-time data tools." },
                { icon: "🗓️", title: "Calendar Integration", desc: "Reads your calendar to find free windows and avoid conflicts before suggesting any dates." },
                { icon: "🔐", title: "Secure Booking", desc: "Encrypted payment processing with explicit user permission gates before any transaction fires." },
              ].map(f => (
                <div key={f.title} style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "16px", padding: "24px" }}>
                  <div style={{ fontSize: "28px", marginBottom: "12px" }}>{f.icon}</div>
                  <div style={{ fontSize: "16px", fontWeight: "700", color: "#e8e4dc", marginBottom: "8px" }}>{f.title}</div>
                  <div style={{ fontSize: "14px", color: "#6b7a8d", lineHeight: "1.6" }}>{f.desc}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ─── PREFERENCES SCREEN ─── */}
        {screen === "preferences" && (
          <div style={{ paddingTop: "48px", paddingBottom: "48px" }}>
            <button onClick={() => setScreen("home")} style={{ background: "none", border: "none", color: "#6b7a8d", cursor: "pointer", marginBottom: "32px", fontSize: "14px", fontFamily: "inherit" }}>← Back</button>
            <h2 style={{ fontSize: "36px", fontWeight: "800", letterSpacing: "-1px", marginBottom: "8px", color: "#fff" }}>Your preferences</h2>
            <p style={{ color: "#6b7a8d", marginBottom: "40px" }}>Help the AI agent understand what you're looking for.</p>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "32px" }}>
              {[
                { label: "🌍 Destination", key: "destination", placeholder: "Bali, Indonesia" },
                { label: "📅 Travel Dates", key: "dates", placeholder: "Jun 14 – Jun 21, 2025" },
                { label: "💰 Budget (USD)", key: "budget", placeholder: "$3,000" },
                { label: "👥 Travelers", key: "travelers", placeholder: "2 adults" },
              ].map(f => (
                <div key={f.key}>
                  <label style={{ display: "block", fontSize: "13px", color: "#6b7a8d", marginBottom: "8px", fontFamily: "monospace" }}>{f.label}</label>
                  <input
                    value={prefs[f.key]}
                    onChange={e => setPrefs({ ...prefs, [f.key]: e.target.value })}
                    placeholder={f.placeholder}
                    style={{ width: "100%", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "10px", padding: "12px 14px", color: "#e8e4dc", fontSize: "15px", fontFamily: "inherit", outline: "none", boxSizing: "border-box" }}
                  />
                </div>
              ))}
            </div>

            <div style={{ marginBottom: "32px" }}>
              <label style={{ display: "block", fontSize: "13px", color: "#6b7a8d", marginBottom: "12px", fontFamily: "monospace" }}>🎨 Travel Style</label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
                {["Beach & Culture", "Adventure", "City Break", "Food Tour", "Wellness", "Family Fun"].map(s => (
                  <button key={s} onClick={() => setPrefs({ ...prefs, style: s })} style={{ background: prefs.style === s ? "rgba(14,154,110,0.2)" : "rgba(255,255,255,0.03)", border: `1px solid ${prefs.style === s ? "#0e9a6e" : "rgba(255,255,255,0.1)"}`, borderRadius: "100px", padding: "8px 18px", color: prefs.style === s ? "#0e9a6e" : "#8899aa", cursor: "pointer", fontSize: "14px", fontFamily: "inherit" }}>{s}</button>
                ))}
              </div>
            </div>

            {/* Payment gate */}
            <div style={{ background: "rgba(14,154,110,0.06)", border: "1px solid rgba(14,154,110,0.2)", borderRadius: "14px", padding: "20px", marginBottom: "32px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "12px" }}>
                <span>🔐</span>
                <span style={{ fontWeight: "700", fontSize: "15px", color: "#0e9a6e" }}>Payment & Booking Permission</span>
              </div>
              <p style={{ fontSize: "13px", color: "#6b7a8d", marginBottom: "16px", lineHeight: "1.6" }}>The AI will only make bookings with your explicit permission. Your card is stored securely (Stripe vault). Each booking requires a confirmation step.</p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px" }}>
                {[
                  { label: "Cardholder Name", key: "name" },
                  { label: "Card Number", key: "card" },
                  { label: "Expiry", key: "expiry" },
                ].map(f => (
                  <div key={f.key}>
                    <label style={{ display: "block", fontSize: "11px", color: "#6b7a8d", marginBottom: "6px" }}>{f.label}</label>
                    <input value={payInfo[f.key]} onChange={e => setPayInfo({ ...payInfo, [f.key]: e.target.value })} style={{ width: "100%", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", padding: "9px 10px", color: "#e8e4dc", fontSize: "13px", fontFamily: "monospace", outline: "none", boxSizing: "border-box" }} />
                  </div>
                ))}
              </div>
            </div>

            <button onClick={startPlanning} style={{ background: "linear-gradient(135deg, #0e9a6e, #059860)", color: "#fff", border: "none", padding: "16px 44px", borderRadius: "14px", fontSize: "17px", fontWeight: "700", cursor: "pointer", fontFamily: "inherit", boxShadow: "0 8px 32px rgba(14,154,110,0.3)" }}>
              🤖 Let the AI Plan My Trip →
            </button>
          </div>
        )}

        {/* ─── PLANNING / AGENT SCREEN ─── */}
        {screen === "planning" && (
          <div style={{ paddingTop: "80px", paddingBottom: "80px", textAlign: "center" }}>
            <div style={{ width: "64px", height: "64px", background: "linear-gradient(135deg, #0e9a6e20, #3b82f620)", border: "1px solid rgba(14,154,110,0.3)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 24px", fontSize: "28px", animation: "pulse 2s infinite" }}>🤖</div>
            <h2 style={{ fontSize: "28px", fontWeight: "800", letterSpacing: "-0.5px", marginBottom: "8px", color: "#fff" }}>Planning your trip...</h2>
            <p style={{ color: "#6b7a8d", marginBottom: "48px" }}>The AI agent is working autonomously across multiple tools</p>

            <div style={{ maxWidth: "480px", margin: "0 auto", textAlign: "left" }}>
              {AGENT_STEPS.map((step, i) => {
                const done = completedSteps.includes(step.id);
                const active = i === stepIndex;
                return (
                  <div key={step.id} style={{ display: "flex", alignItems: "flex-start", gap: "16px", padding: "14px 0", borderBottom: "1px solid rgba(255,255,255,0.04)", opacity: i > stepIndex ? 0.3 : 1, transition: "opacity 0.4s" }}>
                    <div style={{ width: "32px", height: "32px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "14px", background: done ? "rgba(14,154,110,0.2)" : active ? "rgba(59,130,246,0.2)" : "rgba(255,255,255,0.04)", border: `1px solid ${done ? "#0e9a6e" : active ? "#3b82f6" : "rgba(255,255,255,0.1)"}`, flexShrink: 0, transition: "all 0.3s" }}>
                      {done ? "✓" : step.icon}
                    </div>
                    <div>
                      <div style={{ fontSize: "15px", fontWeight: "600", color: done ? "#0e9a6e" : "#e8e4dc", marginBottom: "2px" }}>{step.label}</div>
                      <div style={{ fontSize: "12px", color: "#6b7a8d", fontFamily: "monospace" }}>{step.detail}</div>
                    </div>
                    {active && <div style={{ marginLeft: "auto", display: "flex", gap: "3px", alignItems: "center", paddingTop: "8px" }}>
                      {[0, 1, 2].map(d => (
                        <div key={d} style={{ width: "5px", height: "5px", borderRadius: "50%", background: "#3b82f6", animation: `bounce 1s ${d * 0.15}s infinite` }} />
                      ))}
                    </div>}
                  </div>
                );
              })}
            </div>

            <style>{`
              @keyframes pulse { 0%,100%{box-shadow:0 0 0 0 rgba(14,154,110,0.3)} 50%{box-shadow:0 0 0 16px rgba(14,154,110,0)} }
              @keyframes bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
            `}</style>
          </div>
        )}

        {/* ─── RESULT SCREEN ─── */}
        {screen === "result" && (
          <div style={{ paddingTop: "40px", paddingBottom: "60px" }} ref={plannerRef}>
            {/* Header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "32px", flexWrap: "wrap", gap: "16px" }}>
              <div>
                <div style={{ display: "inline-block", background: "rgba(14,154,110,0.12)", border: "1px solid rgba(14,154,110,0.3)", borderRadius: "100px", padding: "4px 14px", fontSize: "12px", color: "#0e9a6e", marginBottom: "12px", fontFamily: "monospace" }}>✓ Plan Ready</div>
                <h2 style={{ fontSize: "32px", fontWeight: "800", letterSpacing: "-1px", marginBottom: "6px", color: "#fff" }}>7 Days in Bali 🌴</h2>
                <p style={{ color: "#6b7a8d" }}>June 14–21, 2025 · 2 Travelers · {prefs.style}</p>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: "28px", fontWeight: "800", color: "#0e9a6e" }}>${totalCost.toLocaleString()}</div>
                <div style={{ fontSize: "12px", color: "#6b7a8d" }}>Total estimate (excl. flights)</div>
                {!booked ? (
                  <button onClick={() => setBookingMode(true)} style={{ marginTop: "12px", background: "linear-gradient(135deg, #0e9a6e, #059860)", color: "#fff", border: "none", padding: "10px 20px", borderRadius: "10px", fontSize: "14px", fontWeight: "700", cursor: "pointer", fontFamily: "inherit" }}>
                    💳 Book Everything
                  </button>
                ) : (
                  <div style={{ marginTop: "12px", background: "rgba(14,154,110,0.15)", border: "1px solid #0e9a6e", borderRadius: "10px", padding: "8px 16px", fontSize: "13px", color: "#0e9a6e" }}>✓ Fully Booked!</div>
                )}
              </div>
            </div>

            {/* Booking confirmation modal */}
            {bookingMode && !booked && (
              <div style={{ background: "rgba(14,154,110,0.06)", border: "1px solid rgba(14,154,110,0.3)", borderRadius: "16px", padding: "24px", marginBottom: "28px" }}>
                <h3 style={{ fontSize: "18px", fontWeight: "700", color: "#0e9a6e", marginBottom: "8px" }}>🔐 Confirm Booking</h3>
                <p style={{ fontSize: "14px", color: "#8899aa", marginBottom: "16px" }}>Charging <strong style={{ color: "#fff" }}>{payInfo.name}</strong> · {payInfo.card} · Total: <strong style={{ color: "#0e9a6e" }}>${totalCost + 163}</strong></p>
                <div style={{ display: "flex", gap: "12px" }}>
                  <button onClick={() => { setBooked(true); setBookingMode(false); }} style={{ background: "linear-gradient(135deg, #0e9a6e, #059860)", color: "#fff", border: "none", padding: "10px 24px", borderRadius: "10px", fontSize: "14px", fontWeight: "700", cursor: "pointer", fontFamily: "inherit" }}>✓ Confirm & Book</button>
                  <button onClick={() => setBookingMode(false)} style={{ background: "none", border: "1px solid rgba(255,255,255,0.15)", color: "#8899aa", padding: "10px 20px", borderRadius: "10px", fontSize: "14px", cursor: "pointer", fontFamily: "inherit" }}>Cancel</button>
                </div>
              </div>
            )}

            {/* Tabs */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "28px" }}>
              {/* Flights */}
              <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "14px", padding: "20px" }}>
                <div style={{ fontWeight: "700", fontSize: "15px", marginBottom: "14px", color: "#e8e4dc" }}>✈️ Flights</div>
                {FLIGHTS.map((f, i) => (
                  <div key={i} style={{ padding: "12px 0", borderBottom: i < FLIGHTS.length - 1 ? "1px solid rgba(255,255,255,0.05)" : "none" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                      <span style={{ fontSize: "13px", color: "#e8e4dc", fontWeight: "600" }}>{f.airline}</span>
                      <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                        {f.badge && <span style={{ background: "rgba(14,154,110,0.15)", border: "1px solid rgba(14,154,110,0.3)", borderRadius: "100px", padding: "2px 8px", fontSize: "10px", color: "#0e9a6e" }}>{f.badge}</span>}
                        <span style={{ color: "#0e9a6e", fontWeight: "700", fontFamily: "monospace" }}>{f.price}</span>
                      </div>
                    </div>
                    <div style={{ fontSize: "12px", color: "#6b7a8d" }}>{f.from} → {f.to} · {f.time}</div>
                  </div>
                ))}
              </div>

              {/* Hotels */}
              <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "14px", padding: "20px" }}>
                <div style={{ fontWeight: "700", fontSize: "15px", marginBottom: "14px", color: "#e8e4dc" }}>🏨 Hotels</div>
                {HOTELS.map((h, i) => (
                  <div key={i} style={{ padding: "12px 0", borderBottom: i < HOTELS.length - 1 ? "1px solid rgba(255,255,255,0.05)" : "none" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                      <span style={{ fontSize: "13px", color: "#e8e4dc", fontWeight: "600" }}>{h.name}</span>
                      <span style={{ color: "#0e9a6e", fontWeight: "700", fontFamily: "monospace", fontSize: "13px" }}>{h.price}</span>
                    </div>
                    <div style={{ fontSize: "12px", color: "#6b7a8d", marginBottom: "6px" }}>{"⭐".repeat(h.stars)} · {h.location}</div>
                    <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                      {h.features.map(feat => (
                        <span key={feat} style={{ background: "rgba(255,255,255,0.04)", borderRadius: "6px", padding: "2px 8px", fontSize: "11px", color: "#8899aa" }}>{feat}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Day-by-day itinerary */}
            <div style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "16px", overflow: "hidden" }}>
              <div style={{ padding: "20px 24px", borderBottom: "1px solid rgba(255,255,255,0.07)", fontWeight: "700", fontSize: "15px" }}>🗺️ Day-by-Day Itinerary</div>
              {/* Day tabs */}
              <div style={{ display: "flex", gap: "0", overflowX: "auto", borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
                {ITINERARY.map((d, i) => (
                  <button key={i} onClick={() => setActiveDay(i)} style={{ background: activeDay === i ? "rgba(14,154,110,0.12)" : "none", borderBottom: activeDay === i ? "2px solid #0e9a6e" : "2px solid transparent", border: "none", borderBottom: activeDay === i ? "2px solid #0e9a6e" : "2px solid transparent", padding: "12px 20px", color: activeDay === i ? "#0e9a6e" : "#6b7a8d", cursor: "pointer", fontSize: "13px", fontWeight: "600", whiteSpace: "nowrap", fontFamily: "inherit" }}>
                    Day {d.day}
                  </button>
                ))}
              </div>
              {/* Active day content */}
              <div style={{ padding: "24px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
                  <div>
                    <div style={{ fontWeight: "800", fontSize: "20px", color: "#fff", marginBottom: "4px" }}>{ITINERARY[activeDay].title}</div>
                    <div style={{ fontSize: "13px", color: "#6b7a8d" }}>Day {ITINERARY[activeDay].day} of 7</div>
                  </div>
                  <div style={{ background: "rgba(14,154,110,0.12)", border: "1px solid rgba(14,154,110,0.2)", borderRadius: "10px", padding: "8px 14px", textAlign: "center" }}>
                    <div style={{ fontWeight: "700", color: "#0e9a6e", fontFamily: "monospace" }}>{ITINERARY[activeDay].cost}</div>
                    <div style={{ fontSize: "11px", color: "#6b7a8d" }}>est. daily</div>
                  </div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {ITINERARY[activeDay].activities.map((act, j) => (
                    <div key={j} style={{ display: "flex", alignItems: "center", gap: "14px", padding: "12px 14px", background: "rgba(255,255,255,0.03)", borderRadius: "10px" }}>
                      <div style={{ width: "28px", height: "28px", borderRadius: "50%", background: "rgba(14,154,110,0.15)", border: "1px solid rgba(14,154,110,0.2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "12px", color: "#0e9a6e", fontFamily: "monospace", fontWeight: "700", flexShrink: 0 }}>{j + 1}</div>
                      <span style={{ fontSize: "15px", color: "#e8e4dc" }}>{act}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div style={{ marginTop: "24px", padding: "16px 20px", background: "rgba(59,130,246,0.06)", border: "1px solid rgba(59,130,246,0.2)", borderRadius: "12px", fontSize: "13px", color: "#6b7a8d", lineHeight: "1.6" }}>
              <strong style={{ color: "#3b82f6" }}>ℹ️ Demo note:</strong> This is a PoC demonstration. In production, each tool call (flights, hotels, bookings) connects to real APIs via LangGraph agent nodes. Booking actions require payment confirmation and are logged for audit.
            </div>

            <div style={{ marginTop: "16px", display: "flex", gap: "12px" }}>
              <button onClick={() => { setScreen("preferences"); setBooked(false); }} style={{ background: "none", border: "1px solid rgba(255,255,255,0.15)", color: "#8899aa", padding: "10px 20px", borderRadius: "10px", fontSize: "14px", cursor: "pointer", fontFamily: "inherit" }}>← Edit Preferences</button>
              <button onClick={() => { setScreen("home"); setBooked(false); }} style={{ background: "none", border: "1px solid rgba(255,255,255,0.15)", color: "#8899aa", padding: "10px 20px", borderRadius: "10px", fontSize: "14px", cursor: "pointer", fontFamily: "inherit" }}>Start Over</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
