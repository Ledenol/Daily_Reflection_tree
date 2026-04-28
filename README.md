# 🧠 Reflection Agent

A deterministic, tree-based reflection system that guides users through structured introspection using predefined logic and signal-based reasoning.

---

## 📁 Project Structure

```
project/
│
├── agent.py                      ← Core execution engine
├── tree/
│   └── reflection-tree.json      ← Decision tree (questions + logic)
├── transcripts/
│   ├── persona1.md               ← Sample run (victim / external pattern)
│   └── persona2.md               ← Sample run (high ownership pattern)
└── README.md                     ← How to read the tree / run the agent
```

---

## ▶️ How to Run

```bash
python agent.py tree/reflection-tree.json
```

---

## 🌳 How to Read the Tree

The system is driven entirely by a **JSON decision tree**.

Each node represents a step in the reflection flow.

---

### 1. Node Types

#### Start
```json
{ "type": "start" }
```
- Entry point of the reflection

---

#### Question
```json
{
  "type": "question",
  "text": "...",
  "options": [...],
  "signals": { "option": "axis:label" }
}
```

- Displays a question to the user  
- Each answer emits a **signal**  
- Signals are used later for decision-making  

---

#### Decision
```json
{
  "type": "decision",
  "rules": { "answer": "next_node" }
}
```

OR (signal-based):

```json
{
  "type": "decision",
  "rules_signal": {
    "axis": {
      "dominant_label": "next_node"
    }
  }
}
```

- Invisible to the user  
- Routes flow based on:
  - direct answers OR  
  - accumulated signals  

---

#### Reflection
```json
{
  "type": "reflection",
  "text": "..."
}
```

- Displays contextual feedback  
- Triggered after behavioral interpretation  

---

#### Bridge
```json
{
  "type": "bridge",
  "target": "NEXT_NODE"
}
```

- Moves flow between sections (axes)  
- No user input required  

---

#### Summary
```json
{
  "type": "summary",
  "text": "..."
}
```

- Final reflection output  
- Can be static or dynamic  

---

#### End
```json
{ "type": "end" }
```

- Terminates the session  

---

## 🧠 Signal System (Core Idea)

Instead of branching on single answers, the system uses:

```
answers → signals → aggregation → dominant behavior → decision
```

### Example:
```json
"Blame external factors" → axis1:external
"Figure out what I can control" → axis1:internal
```

Final decision:
```
dominant(axis1) → internal OR external
```

---

## 🔄 Flow Overview

```
START
  ↓
Axis 1 (Control)
  ↓
Axis 2 (Contribution)
  ↓
Axis 3 (Perspective)
  ↓
SUMMARY
  ↓
END
```

Each axis:
- asks questions  
- collects signals  
- determines dominant behavior  
- gives reflection  

---

## 📊 What This System Demonstrates

- Deterministic agent design  
- Stateful reasoning  
- Behavior modeling without LLMs  
- Clean separation of logic and execution  

---

## ⚠️ Notes

- No external APIs required  
- Fully offline  
- Behavior is entirely controlled by the JSON tree  

---

## 🚀 Next Steps (Optional)

- Add dynamic summaries  
- Build UI (React / CLI enhancements)  
- Visualize decision paths  
- Extend axes or add personalization  

---