# 🧠 TinyManus: A Lightweight Multi-Agent Collaboration Framework

**TinyManus** is a minimal, extensible multi-agent orchestration framework designed for LLM-based task collaboration. It provides a clean agent abstraction, task-level flow control, and session-based context sharing, with support for both user-specified workflows and automated planning.

---

## 🚀 Features

- ✅ **Simple Agent Interface**  
  Agents are decoupled from orchestration logic — just implement `run(request: str) -> str`.

- 🧩 **Task-Centric Workflow**  
  Each task is bound to one agent and managed through a `Session`-level flow controller.

- 🔀 **Hybrid Execution Plan**  
  Supports mixed sequential and parallel execution like `[[Task1, Task2], [Task3]]`.

- 🧠 **Planner Optional**  
  Use a `PlannerAgent` to auto-generate task flows, or manually define them for full control.

- 📝 **Prompt Injection with Context**  
  Prompts are dynamically constructed using a template with prior task history.

- 📊 **Logging & Monitoring**  
  Emoji-enhanced logging helps track execution in real time.

---


## 🧪 Minimal Example

```python
agentA = ReActAgent("AgentA")
agentB = ReActAgent("AgentB")
agentC = ReActAgent("AgentC")

template = TaskPromptTemplate("""
You are a member of a multi-agent collaboration system.
Your current task:
----
{task}
----
Previous task history:
----
{history}
----
""")

session = Session("TinyDemo", template)

session.set_task_flow([
    [Task("Introduce TinyManus", agentA), Task("Give a use case", agentB)],
    [Task("Summarize the above", agentC)]
])

await session.run()
```

---

## 📁 Project Structure

```
TinyManus/
├── agent/                  # Core agent definitions
│   ├── base.py             # BaseAgent interface
│   ├── one_shot.py         # One-shot agent variant
│   └── react.py            # ReAct-based agent logic
├── memory/                 # Memory backend
│   └── memory.py
├── prompt/                 # Prompt templates
│   ├── react_prompt.py
│   └── template.py         # Shared prompt template
├── test/                   # (Reserved for unit tests)
├── tools/                  # Built-in tools
│   ├── base.py
│   ├── google_search.py
│   ├── terminator.py
│   ├── tool_collection.py  # Tool registry
│   └── cmd/                # Shell-based tools
│       ├── shell_tool.py
│       └── shell_session.py
├── utils/
│   └── logger.py           # Logging utilities
├── workflow/               # Task/session orchestration
│   ├── session.py
│   └── task.py
├── llm.py                  # LLM interfaces or wrappers
├── main.py                 # Entry point
├── LICENSE
└── README.md

```

---

## 🔮 Coming Soon

- [ ] Task timeout / retry control
- [ ] DAG-based execution planning
- [ ] Visual session dashboard
- [ ] Toolchain system enhancements
- [ ] MCP (Model Context Protocol) support
- [ ] Multi-agent debate mode with training data generation
- [ ] And More...

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change or improve.

---

## 🧑‍💻 Author

Created by [Zhiyu Zhang](https://github.com/ZhiyuZhangA), UC Davis.

---

## 🪄 License

Apache 2.0 License. See [LICENSE](./LICENSE) for details.
