import { useState } from "react";
import "./App.css";

const initialState = {
  name: null,
  language: null,
  budget: null,
  preferred_location: null,
  property_type: null,
  buying_purpose: null,
  purchase_timeline: null,
  site_visit_requested: false,
  site_visit_date: null,
  site_visit_time: null,
  booking_status: null,
  human_escalation_requested: false,
  escalation_id: null,
  follow_up_requested: false,
  follow_up_time: null,
  follow_up_id: null,
};

function App() {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [state, setState] = useState(initialState);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!message.trim() || loading) {
      return;
    }

    const customerMessage = message.trim();

    setMessages((current) => [
      ...current,
      { role: "customer", content: customerMessage },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: customerMessage,
          state,
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to reach the backend.");
      }

      const data = await response.json();

      setState(data.state);

      setMessages((current) => [
        ...current,
        { role: "agent", content: data.response },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: "agent",
          content: "I couldn't connect to the sales agent. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">HUVO AI</p>
          <h1>AI Sales Agent</h1>
        </div>

        <div className="status">
          <span className="status-dot" />
          Agent Online
        </div>
      </header>

      <main className="dashboard">
        <section className="chat-panel">
          <div className="panel-header">
            <div>
              <h2>Lead Conversation</h2>
              <p>Real-time qualification and sales assistance</p>
            </div>
          </div>

          <div className="messages">
            {messages.length === 0 && (
              <div className="empty-state">
                <h3>Start a conversation</h3>
                <p>
                  Try something like “I am looking for a 3 BHK under 1.5 crore.”
                </p>
              </div>
            )}

            {messages.map((item, index) => (
              <div
                key={`${item.role}-${index}`}
                className={`message-row ${item.role}`}
              >
                <div className="message-bubble">{item.content}</div>
              </div>
            ))}

            {loading && (
              <div className="message-row agent">
                <div className="message-bubble typing">Thinking...</div>
              </div>
            )}
          </div>

          <div className="composer">
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a customer message..."
              rows={2}
            />

            <button onClick={sendMessage} disabled={loading}>
              Send
            </button>
          </div>
        </section>

        <aside className="sidebar">
          <div className="side-card">
            <div className="card-title">
              <h2>Lead Profile</h2>
              <span>Live</span>
            </div>

            <InfoRow label="Name" value={state.name} />
            <InfoRow label="Language" value={state.language} />
            <InfoRow label="Budget" value={state.budget} />
            <InfoRow label="Property" value={state.property_type} />
            <InfoRow label="Location" value={state.preferred_location} />
            <InfoRow label="Purpose" value={state.buying_purpose} />
            <InfoRow label="Timeline" value={state.purchase_timeline} />
          </div>

          <div className="side-card">
            <h2>Conversation Outcomes</h2>

            <div className="outcome">
              <span>Site Visit</span>
              <strong>
                {state.booking_status || "Not requested"}
              </strong>
            </div>

            <div className="outcome">
              <span>Follow Up</span>
              <strong>
                {state.follow_up_requested ? "Scheduled" : "Not requested"}
              </strong>
            </div>

            <div className="outcome">
              <span>Human Escalation</span>
              <strong>
                {state.human_escalation_requested ? "Requested" : "Not requested"}
              </strong>
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="info-row">
      <span>{label}</span>
      <strong>{value || "Not captured"}</strong>
    </div>
  );
}

export default App;