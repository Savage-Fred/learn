# Learn Platform MCP Server Instructions

Use `learn_get_topic` and `learn_get_exercise` to retrieve real curriculum and
rubrics. Teach, conduct practice interviews and assess in the connected client;
the MCP server does not call another model. Record an evidence-based client
assessment with `learn_record_assessment`, using one stable ID per answer.
Read shared history with `learn_get_progress`, pin topics, and distill technical
knowledge with `learn_record_durable_learning`. That tool writes a markdown file,
without a git commit. Personal assessment state stays outside git in
`LEARN_DATA_DIR`. See `docs/mcp.md` for installation and client connection details.
