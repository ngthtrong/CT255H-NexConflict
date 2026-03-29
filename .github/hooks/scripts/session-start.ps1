$result = @{
  continue = $true
  systemMessage = "Agentic policy active: follow branch guard, workflow docs in .github-copilot/commands, and required human checkpoints."
}

$result | ConvertTo-Json -Compress
