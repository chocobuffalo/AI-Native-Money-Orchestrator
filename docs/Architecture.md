title AI-Native Fintech Money Movement Orchestrator

// LEVEL 1 — Ingestion Layer
User UI [icon: monitor]

Signal Ingestion Layer [color: blue, icon: download] {
  Transactional Metadata [icon: file-text, label: "Transactional Metadata"]
  User Behavioral Context [icon: activity, label: "Behavioral Context"]
  External Signals [icon: globe, label: "External Signals"]
  Context Bundle [icon: package, label: "Context Bundle"]
}

// LEVEL 2 — Hybrid Brain
Hybrid Brain [color: purple, icon: cpu] {
  Gate A Hard Rules [icon: shield, label: "Gate A: Hard Rules Engine"] {
    Regulatory Limits [icon: alert-triangle, label: "Regulatory Limits"]
    Daily Monthly Caps [icon: calendar, label: "Daily/Monthly Caps"]
    AML KYC Check [icon: user-check, label: "AML/KYC Check"]
    Blocked Accounts [icon: slash, label: "Blocked Accounts"]
    Time Restrictions [icon: clock, label: "Time Restrictions"]
  }
  
  Gate B Cognitive Scorer [icon: openai, label: "Gate B: Cognitive Risk Scorer 🧠"] {
    Behavioral Analysis [icon: trending-up, label: "Behavioral Analysis"]
    Risk Output [icon: bar-chart-2, label: "Risk Score Output"]
    LLM Guardrail Layer [icon:shield-off, label:"LLM Guardrail Layer"]
  }
  
  Hard Block [icon: x-circle, label: "Hard Block ❌"]
  Fallback Engine [icon:refresh-cw, label:"Fallback Engine"]
}

// LEVEL 3 — Decision Orchestrator
Decision Orchestrator [color: orange, icon: git-branch] {
  Green Path [icon: check-circle, color: green, label: "Green Path (<10%)"]
  Yellow Path [icon: alert-circle, color: yellow, label: "Yellow Path (10-70%)"]
  Red Path [icon: x-octagon, color: red, label: "Red Path (>70%)"]
}

Mock Banking API [icon: aws-api-gateway, label: "Mock Banking API"]
Temporary Hold [icon: pause-circle, label: "Temporary Hold"]
LLM Explanation Generator [icon: openai, label: "LLM Explanation 🧠"]
Human Dashboard [icon: users, label: "Security Dashboard 👤"]

// LEVEL 4 — Transparency & Feedback
Transparency Layer [color: green, icon: message-circle] {
  Human Readable Output [icon: openai, label: "LLM Translator 🧠"]
}

// SIDECARS
Observability Sidecar [color: gray, icon: eye] {
  Audit DB [icon: database, label: "Audit Trail DB"]
}

Policy Store [color: gray, icon: settings] {
  Thresholds [icon: sliders, label: "Adjustable Thresholds"]
  Business Rules [icon: book, label: "Business Rules"]
}
Context Normalizer [icon:filter, label:"Context Normalizer"]
Additional Info Module [icon:help-circle, label:"User Additional Info Request"]
Status Engine [icon:git-commit, label:"Status Engine"]
  Status Needs Info [icon:help-circle, label:"Needs Info"]
  Status Blocked [icon:x, label:"Blocked"]
  Status Held [icon:pause, label:"Held"]
  Status Approved [icon:check, label:"Approved"]
Security Event Stream [icon:alert-octagon, label:"Security Event Stream"]
Business Continuity Fallback [icon:life-buoy, label:"Continuity Fallback"]

// === CONNECTIONS ===

// Level 1 Flow
Transactional Metadata > Context Bundle
User Behavioral Context > Context Bundle
External Signals > Context Bundle

// Level 1 to Level 2
Context Bundle > Gate A Hard Rules: validate

// Gate A Internal Flow
Regulatory Limits > Daily Monthly Caps
Daily Monthly Caps > AML KYC Check
AML KYC Check > Blocked Accounts
Blocked Accounts > Time Restrictions

// Gate A Outcomes
Time Restrictions > Gate B Cognitive Scorer: rules passed
Time Restrictions > Hard Block: rule failed [color: red]

// Gate B Internal

// Level 2 to Level 3
Risk Output > Decision Orchestrator: risk assessment

// Decision Orchestrator Branches

// Green Path
Green Path > Mock Banking API: approve [color: green]

// Yellow Path
Yellow Path > Temporary Hold [color: orange]
Temporary Hold > LLM Explanation Generator [color: orange]

// Red Path
Human Dashboard > Mock Banking API: approve 👤 [color: green]
Human Dashboard > Hard Block: reject 👤 [color: red]

// Transparency Layer
Mock Banking API > Human Readable Output

// Feedback Loop
Human Dashboard --> Policy Store: threshold updates [color: purple]
Human Dashboard --> Gate B Cognitive Scorer: model refinement [color: purple]

// Policy Store Connections
Policy Store --> Gate A Hard Rules: rules config
Policy Store --> Decision Orchestrator: threshold config

// Observability - Audit Trail
Signal Ingestion Layer --> Audit DB: log [color: gray]
Gate A Hard Rules --> Audit DB: log [color: gray]
Gate B Cognitive Scorer --> Audit DB: log [color: gray]
Decision Orchestrator --> Audit DB: log [color: gray]
Human Dashboard --> Audit DB: log [color: gray]
Human Readable Output --> Audit DB: log [color: gray]

legend {
  [connection: ">", label: "Primary data flow"]
  [connection: ">", color: green, label: "Approved transaction"]
  [connection: ">", color: red, label: "Blocked/rejected"]
  [connection: ">", color: orange, label: "Held for review"]
  [connection: "-->", color: purple, label: "Feedback loop"]
  [connection: "-->", color: gray, label: "Audit logging"]
  [icon: openai, label: "AI/LLM Component 🧠"]
  [icon: users, label: "Human-in-the-Loop 👤"]
  [color: gray, label: "Sidecar services"]
}
User UI < LLM Explanation Generator: request info
Human Dashboard < Red Path: escalate
User UI < Human Readable Output: explain decision
User UI > Context Normalizer: clean & validate
Context Normalizer > Transactional Metadata
Context Normalizer > User Behavioral Context
Context Normalizer > External Signals
Behavioral Analysis > LLM Guardrail Layer: validate
LLM Guardrail Layer > Risk Output: safe output
LLM Guardrail Layer > Fallback Engine: LLM failure [color: red]
Fallback Engine > Decision Orchestrator: fallback assessment
Yellow Path > Additional Info Module: request info [color: orange]
Additional Info Module > LLM Explanation Generator [color: orange]
Temporary Hold > Additional Info Module [color: orange]
Decision Orchestrator > Status Engine: set status
Status Engine > Transparency Layer: status update
Red Path > Security Event Stream: emit event [color: red]
Security Event Stream > Audit DB: log [color: gray]
Policy Store > Gate A Hard Rules: rules config
Policy Store > Gate B Cognitive Scorer: scorer config
Status Engine > User UI: display status
LLM Guardrail Layer > Business Continuity Fallback: LLM failure
Decision Orchestrator > Business Continuity Fallback: orchestration failure
Mock Banking API > Business Continuity Fallback: banking failure
Business Continuity Fallback > Status Engine: safe fallback status