# Use Learn from your AI subscription

The connected AI client teaches, asks questions and evaluates your answers.
Learn's MCP server supplies real curriculum, rubrics and shared learning history.
This path invokes no model CLI, paid API or fallback model. Usage follows the
connected platform's plan and limits; MCP does not pool subscription quotas.

## Install once

Use the implementation checkout containing `app/`, not the initial primary
checkout. Run from that implementation checkout with Python 3.13:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

Use the absolute path to `.venv/bin/learn-mcp` below. It works from any working
directory. All clients on this host share `~/.local/share/learn`; set
`LEARN_DATA_DIR` consistently to use another directory outside the repository.
An editable install keeps the curriculum available alongside the application.

## Connect local clients

Replace `/absolute/path/to/learn` with your implementation checkout.

**Codex:**

```sh
codex mcp add learn -- /absolute/path/to/learn/.venv/bin/learn-mcp
```

Restart the client or open a fresh conversation, then inspect `/mcp`. A manual
configuration is in `app/plugins/codex/config_snippet.toml`. Codex supports stdio
and Streamable HTTP. [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp).

**Claude Code:**

```sh
claude mcp add --transport stdio learn -- /absolute/path/to/learn/.venv/bin/learn-mcp
```

**Claude Desktop:** merge this into its MCP configuration on the machine where
the server is installed, then restart Desktop:

```json
{
  "mcpServers": {
    "learn": {"command": "/absolute/path/to/learn/.venv/bin/learn-mcp"}
  }
}
```

**Gemini CLI:** use the same `mcpServers` JSON in `.gemini/settings.json`, merging
with existing settings. A template is in `app/plugins/gemini/settings.json`.
[Gemini CLI MCP configuration](https://geminicli.com/docs/tools/mcp-server/).

These examples add a server; they do not replace your existing client settings.
The server uses the [official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
for protocol negotiation and transports. Both the installed `learn-mcp` command
and `python -m app.mcp` launch this server.

## Use it

Try this in the connected AI conversation:

> Use Learn to teach me algorithms. Read the curriculum and a starter exercise,
> ask me one question at a time, and wait for my answer. Evaluate it against the
> supplied rubric, explain the gaps, and record your assessment. Then choose a
> harder or easier real exercise based on my answer. Pin topics I should revisit.

Available tools:

| Tool | Purpose |
| --- | --- |
| `learn_list_topics` | Discover the curriculum |
| `learn_get_topic` | Read fundamentals, sources, rubrics and exercises |
| `learn_get_exercise` | Read a complete exercise at starter/L4/L5/L6 |
| `learn_get_progress` | Read shared pins, recent assessments and existing app ratings |
| `learn_record_assessment` | Persist the client's score, feedback and learner answer |
| `learn_pin_topic` | Maintain the study queue |
| `learn_get_pinned_topics` | Retrieve that queue |
| `learn_record_durable_learning` | Write distilled technical knowledge to topic markdown |

An assessment is the connected AI's judgment, identified as
`connected_ai_client`. Use a stable `assessment_id` per answer: identical retries
return the existing record; changed content with the same ID is rejected.
Personal answers and scores stay outside git. They do not silently change the
web app's legacy ratings. Durable notes write curriculum files without committing
them; exclude personal performance and resume information from those notes.

## HTTP clients and browser apps

The standalone server supports Streamable HTTP at `/mcp`, on a separate port
from the web application's legacy endpoints:

```sh
.venv/bin/learn-mcp --transport streamable-http --port 8797
```

This binds to loopback. If `LEARN_API_TOKEN` is set in the server environment,
every HTTP request requires `Authorization: Bearer <token>`, including requests
arriving from a loopback proxy. Tokens in query strings are not accepted.
Non-loopback binding requires that token. For a reverse proxy, add its exact
public host (including port if nonstandard) to `LEARN_MCP_ALLOWED_HOSTS`;
the SDK's Host and Origin protections remain enabled. Keep tokens out of git.

**ChatGPT:** a private server can connect through Secure MCP Tunnel, including
stdio, without public exposure. Follow the account's tunnel setup and choose the
tunnel under the custom MCP server's Connection settings. Public connections use
HTTPS and require suitable authentication discovery for private tools. Do not
select anonymous public access for this personal-state server.
[Connect and test](https://developers.openai.com/plugins/deploy/connect-chatgpt),
[Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

**Claude web/mobile:** custom remote connectors originate in Anthropic's cloud;
localhost or a private Tailnet URL alone will not connect. They require a
reachable HTTPS endpoint. Configure a fixed request header for the server's
bearer token if using the supported header-auth connection flow. This server
does not implement an OAuth authorization server.
[Claude custom connectors](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

Account linking, tunnel creation and public hosting are separate from running
the server. Neither browser platform is claimed connected merely because local
MCP tests pass. Gemini CLI is covered here; no Gemini web-app connector is claimed.

The web application's existing `/mcp/call` and SSE routes remain legacy paths;
they retain their old tool behavior. Use the standalone SDK server described
above for subscription-client learning and assessment.

## Existing stdio clients

The default `learn-mcp` and `python -m app.mcp` commands now expose the client-owned
tool inventory above. Existing clients must restart and rediscover tools; update
pinning calls from `topic_slug` to `topic_id`. The old server-generated quiz,
interview and job-analysis tools are absent from this new contract.

For an existing integration that still requires those legacy tools, explicitly run
the installed environment's Python with `-m app.mcp.transports.stdio`. That legacy
server keeps the previous contract and heuristic behavior. The static Antigravity
schemas in `app/plugins/antigravity/mcp/schemas/` describe only that legacy server;
current clients should discover tool schemas from the SDK server itself.
