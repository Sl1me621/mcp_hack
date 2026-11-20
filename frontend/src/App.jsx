import { useState } from "react";

const A2A_ENDPOINT = "http://127.0.0.1:8001/a2a";

function generateSessionId() {
  if (crypto?.randomUUID) return crypto.randomUUID();
  return `session-${Math.random().toString(16).slice(2)}-${Date.now()}`;
}

function MessageCard({ message }) {
  const role = message?.role || "unknown";
  const isUser = role === "user";
  const isAgent = role === "agent";
  const isTool = role === "tool";

  const textSegment = message?.contents?.find((c) => c.type === "text");
  const toolSegments = (message?.contents || []).filter(
    (c) => c.type === "tool_result"
  );

  const roleLabel =
    {
      user: "USER",
      agent: "AGENT",
      tool: "TOOL",
    }[role] || role.toUpperCase();

  return (
    <div className={`message-card ${role}`}>
      <div className="message-header">
        <span className="pill">{roleLabel}</span>
        {isTool && toolSegments[0]?.tool_name ? (
          <span className="tool-name">{toolSegments[0].tool_name}</span>
        ) : null}
      </div>

      {isTool ? (
        toolSegments.length > 0 ? (
          toolSegments.map((segment, idx) => (
            <details key={idx} className="tool-result" open>
              <summary>Результат MCP</summary>
              <pre>{JSON.stringify(segment.tool_output, null, 2)}</pre>
            </details>
          ))
        ) : (
          <div className="text-muted">Нет данных MCP</div>
        )
      ) : (
        <p className="message-text">
          {textSegment?.text || "— пустое сообщение —"}
        </p>
      )}

      {message?.error ? (
        <p className="error-text">{message.error}</p>
      ) : null}
    </div>
  );
}

function MessageList({ messages }) {
  if (!messages.length) {
    return (
      <div className="empty">
        Начните диалог, чтобы увидеть работу MCP и агента.
      </div>
    );
  }

  return (
    <div className="message-list">
      {messages.map((msg, idx) => (
        <MessageCard key={idx} message={msg} />
      ))}
    </div>
  );
}

function Composer({ value, onChange, onSend, loading }) {
  return (
    <div className="composer">
      <textarea
        placeholder='Напишите запрос, пример: "calc: 2 + 2 * 3"'
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            onSend();
          }
        }}
        disabled={loading}
      />
      <button onClick={onSend} disabled={loading || !value.trim()}>
        {loading ? "Отправка..." : "Отправить"}
      </button>
    </div>
  );
}

export default function App() {
  const [sessionId] = useState(() => generateSessionId());
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMessage = {
      role: "user",
      contents: [{ type: "text", text: trimmed }],
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setInput("");

    try {
      const response = await fetch(A2A_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          messages: [userMessage],
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      const newMessages = Array.isArray(data?.messages)
        ? data.messages
        : null;

      if (!newMessages) {
        throw new Error("Непредвиденный формат ответа от A2A");
      }

      setMessages((prev) => [...prev, ...newMessages]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          contents: [
            {
              type: "text",
              text: `Ошибка при запросе: ${err.message}`,
            },
          ],
          error: err.message,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <div className="tag">MCP + A2A Visualizer</div>
          <h1>Диалог с агентом</h1>
          <p className="subtitle">
            Отправьте запрос, агент вызовет MCP-инструмент при необходимости и
            покажет результат.
          </p>
        </div>
        <div className="session">
          <span className="label">Session</span>
          <code>{sessionId}</code>
        </div>
      </header>

      <main>
        {loading ? <div className="status">Запрос выполняется...</div> : null}
        <MessageList messages={messages} />
      </main>

      <Composer
        value={input}
        onChange={setInput}
        onSend={sendMessage}
        loading={loading}
      />
    </div>
  );
}
