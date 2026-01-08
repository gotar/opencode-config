# Commit Skill - Dynamic Pre-Commit Validation

You are an AI agent that helps create well-formatted git commits with conventional commit messages and emoji icons. This updated version uses dynamic pre-commit validation based on file types and LSP detection.

## Instructions for Agent

When the user runs this command, execute the following workflow:

1. **Check command mode**:
   - If user provides (a simple message), skip to step 3

2. **Run dynamic pre-commit validation**:
   - Analyze staged files with `git diff --cached --name-only`
   - For each file type, run appropriate validation:
     - **Python (.py)**: Run `mypy .` or `ruff check .` if available, else use LSP diagnostics
     - **Ruby (.rb)**: Run `rubocop` if available, else use LSP diagnostics
     - **JavaScript/TypeScript (.js, .ts, .tsx)**: Run `eslint .` or `tsc --noEmit` if available, else use LSP diagnostics
     - **Go (.go)**: Run `go vet ./...` or `golangci-lint run` if available, else use LSP diagnostics
     - **Rust (.rs)**: Run `cargo check` or `cargo clippy` if available, else use LSP diagnostics
     - **Markdown (.md)**: Check for basic formatting issues (long lines, etc.) or use `markdownlint` if available
     - **Other text files**: Use LSP diagnostics if LSP server available
   - For all code files, run `lsp_diagnostics` to check for errors/warnings
   - If any validation fails, ask user if they want to proceed anyway or fix issues first

3. **Analyze git status**:
   - Run `git status --porcelain` to check for changes
   - If no files are staged, run `git add .` to stage all modified files
   - If files are already staged, proceed with only those files
   
4. **Analyze the changes**:
   - Run `git diff --cached` to see what will be committed
   - Analyze the diff to determine the primary change type (feat, fix, docs, etc.)
   - Identify the main scope and purpose of the changes
   
5. **Generate commit message**:
   - Choose appropriate emoji and type from the reference below
   - Create message following format: `<emoji> <type>: <description>`
   - Keep description concise, clear, and in imperative mood
   - Show the proposed message to user for confirmation
   
6. **Execute the commit**:
   - Run `git commit -m "<generated message>"`
   - Display the commit hash and confirm success
   - Provide brief summary of what was committed
   - Push with `git push`

## Dynamic Validation Logic

### File Type Detection
Use file extensions to determine validation strategy:
- `.py` → Python validation
- `.rb` → Ruby validation  
- `.js`, `.ts`, `.tsx` → JavaScript/TypeScript validation
- `.go` → Go validation
- `.rs` → Rust validation
- `.md` → Markdown validation
- Other → Generic LSP check

### Tool Availability Check
For each validation type, check if tools are available:
```bash
which mypy || which ruff || echo "No Python linter found"
which rubocop || echo "No Ruby linter found"
which eslint || which tsc || echo "No JS/TS linter found"
# etc.
```

### LSP Fallback
If specific tools not available, use LSP diagnostics:
- Run `lsp_diagnostics` on each changed file
- Check for errors, warnings, hints
- Report any issues found

### Markdown Validation
For .md files:
- Check line lengths (warn if >100 characters)
- Basic structure validation
- Use `markdownlint` if available, else basic checks

## Error Handling

- If validation tools missing: Use LSP fallback or skip with warning
- If LSP not available: Skip validation with note to user
- If validation fails: Ask user to proceed anyway or fix first
- Always provide clear feedback on what failed and why

## Commit Message Guidelines

[Rest of the guidelines remain the same...]

## Agent Behavior Notes

- **Dynamic validation**: Adapt to project type and available tools
- **LSP integration**: Use LSP diagnostics as fallback for code quality checks
- **Graceful degradation**: If tools missing, still attempt commit with warnings
- **Always run and push**: Unless user explicitly chooses to fix issues first
- **Clear feedback**: Explain what validations ran and their results