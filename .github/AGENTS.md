# Agent Registry for GitHub Copilot

Tài liệu này là bản đồ nhanh để Copilot và team hiểu cách map role sang custom agents.

## Agent map
- BA -> `.github/agents/ba.agent.md`
- PM -> `.github/agents/pm.agent.md`
- Developer -> `.github/agents/developer.agent.md`
- Tech Lead -> `.github/agents/techlead.agent.md`
- Tester -> `.github/agents/tester.agent.md`
- Analyst -> `.github/agents/analyst.agent.md`
- Doc Sync -> `.github/agents/docsync.agent.md`
- Orchestrator -> `.github/agents/orchestrator.agent.md`

## Rule
- Mỗi agent chỉ giải quyết một loại trách nhiệm chính.
- Nếu task lớn, Orchestrator được phép delegate cho subagent phù hợp.
- Phần source-of-truth của workflow vẫn ở `.github-copilot/commands/`.
