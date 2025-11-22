import { useState } from "react";

type BackendResponse = {
  message: string;
  steps: string[];
};

function App() {
  const [input, setInput] = useState<string>("");
  const [response, setResponse] = useState<BackendResponse | null>(null);

  async function sendRequest() {
    try {
      const res = await fetch("http://localhost:8000/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
      });
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error("Error sending request:", err);
    }
  }

  return (
    <div style={{ padding: 40 }}>
      <h2>Compliance Assistant</h2>
      <textarea
        rows={4}
        cols={50}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter request here"
      />
      <br />
      <button onClick={sendRequest}>Submit</button>
      {response && (
        <pre style={{ marginTop: 20 }}>{JSON.stringify(response, null, 2)}</pre>
      )}
    </div>
  );
}

export default App;
