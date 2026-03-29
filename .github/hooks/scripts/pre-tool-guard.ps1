$inputRaw = [Console]::In.ReadToEnd()
$lower = $inputRaw.ToLowerInvariant()

$denyPatterns = @(
  "git reset --hard",
  "git checkout --",
  "git clean -fd",
  "git push origin main",
  "git push origin develop"
)

$matched = $null
foreach ($pattern in $denyPatterns) {
  if ($lower -match [Regex]::Escape($pattern)) {
    $matched = $pattern
    break
  }
}

if ($matched) {
  $deny = @{
    hookSpecificOutput = @{
      hookEventName = "PreToolUse"
      permissionDecision = "deny"
      permissionDecisionReason = "Blocked by policy hook: '$matched' is not allowed in this workspace."
    }
  }
  $deny | ConvertTo-Json -Compress
  exit 0
}

$allow = @{
  hookSpecificOutput = @{
    hookEventName = "PreToolUse"
    permissionDecision = "allow"
    permissionDecisionReason = "No restricted command detected."
  }
}

$allow | ConvertTo-Json -Compress
