# Pluggable Target Adapters

Target adapters establish communication with the AI application under test. This page explains how to configure and use each built-in adapter.

---

## 1. Mock Adapter (`mock`)

The **Mock Adapter** is designed for local demonstration runs, quick prototyping, and fast unit tests. It requires zero API keys or external services.

### Configuration
```yaml
target:
  type: mock
```

### Under the Hood
It maps exact or partial string keywords to pre-defined responses (such as Thai refund policies, standard shipping durations, or prompt injection blocks) with a simulated response latency (e.g. 15-50ms).

---

## 2. HTTP Adapter (`http`)

The **HTTP Adapter** connects to external web endpoints. This is standard for production bots, FastAPI backends, LangChain webhooks, or Flowise API runners.

### Configuration
```yaml
target:
  type: http
  url: "https://api.mychat.com/v1/chat"
  method: "POST"             # GET or POST (default POST)
  input_key: "message"        # Body payload input key
  output_key: "response.text" # Expected response text key (supports dot notation)
  sources_key: "citations"    # Expected citation array key (supports dot notation)
  headers:
    Authorization: "Bearer my-secret-token"
    Content-Type: "application/json"
```

### Invocation Payload
When a test case runs, the adapter fires a JSON payload:

```json
{
  "message": "What is your refund policy?"
}
```

### Expected Response Format
It expects a JSON response body containing the outputs and citations:

```json
{
  "response": {
    "text": "Products are returnable within 7 days."
  },
  "citations": ["refund_policy.md"]
}
```

---

## 3. Command Adapter (`command`)

The **Command Adapter** launches local scripts or command-line programs. This allows you to evaluate models, locally run agents, or microservices without standing up an HTTP server.

### Configuration
```yaml
target:
  type: command
  command: "python path/to/my_agent.py"
  output_key: "answer"
  sources_key: "docs"
```

### Passing Input Parameters

To ensure safety and protect against shell injections, **AgentAudit strictly executes processes with `shell=False`**.

Input parameters are routed in one of two ways:
1.  **Standard Input (stdin)**: If the command *does not* contain the `{input}` placeholder, the case prompt is passed directly to the script via standard input.
2.  **Token replacement**: If the command contains `{input}`, AgentAudit replaces the placeholder inside shlex tokens.
    ```yaml
    target:
      type: command
      command: "python my_agent.py --prompt \"{input}\""
    ```

### Parsing Outputs
If the CLI script outputs raw text, AgentAudit captures it as the response. If the script outputs a valid JSON string (e.g. `{"answer": "...", "docs": []}`), AgentAudit automatically decodes it using your configured output and citation keys.
