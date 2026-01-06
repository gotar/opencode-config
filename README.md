# OpenCode Configuration

OpenCode AI configuration with specialized agents, commands, context standards, and skills.

## Overview

This repository contains the complete OpenCode configuration setup including:
- **Agents**: Specialized AI agents for different workflows
- **Commands**: Custom slash commands for common operations
- **Context**: Project standards and workflow guidelines
- **Skills**: Reusable skill modules for specialized tasks

## Installation

1. Clone this repository:
```bash
git clone https://github.com/gotar/opencode-config ~/.config/opencode
```

2. Install dependencies:
```bash
cd ~/.config/opencode
npm install
```

3. Copy the example environment file and add your API keys:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory (excluded from git):

```env
# Context7 API key for documentation search
CONTEXT7_API_KEY=your_context7_api_key_here
```

### Main Config Files

- **`opencode.json`**: Main OpenCode configuration (MCP servers, models, plugins)
- **`dcp.jsonc`**: DCP plugin configuration
- **`oh-my-opencode.json`**: OhMyOpenCode plugin settings

## Structure

```
.
├── agent/              # AI agent definitions
│   ├── openagent.md    # Universal primary agent
│   ├── opencoder.md    # Coding specialist
│   ├── orchestrator.md # Workflow coordinator
│   └── worker.md      # Task execution agent
├── command/            # Slash commands
│   ├── commit.md       # Commit workflow
│   ├── test.md         # Testing pipeline
│   ├── deploy.md       # Deployment with Kamal
│   └── swarm.md       # Multi-agent orchestration
├── context/            # Standards and workflows
│   └── core/
│       ├── standards/  # Code, docs, tests standards
│       └── workflows/  # Review, delegation workflows
├── skills/             # Reusable skill modules
│   ├── docx/           # Word document processing
│   ├── pptx/           # PowerPoint operations
│   ├── pdf/            # PDF manipulation
│   └── frontend-design/ # UI/UX patterns
├── opencode.json       # Main config
├── .gitignore          # Git exclusions
└── README.md           # This file
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/commit` | Create conventional commits with emoji |
| `/context` | Analyze project structure and patterns |
| `/test` | Run complete Rails testing pipeline |
| `/deploy` | Deploy using Kamal (async) |
| `/swarm` | Start multi-agent workflow |
| `/optimize` | Code performance and security analysis |
| `/plan` | Plan Rails features with multi-tenant architecture |

## MCP Servers

The configuration connects to several MCP servers:

- **Context7**: Documentation search and code examples
- **Chrome DevTools**: Browser automation and testing
- **Tiger PostgreSQL**: Database documentation and guidance

## Skills

This config includes various skills for specialized tasks:

- **Document Processing**: DOCX, PPTX, PDF operations
- **Design**: Canvas design, frontend UI/UX patterns
- **Development**: Rails Basecamp engineering, MCP builder
- **Communication**: Internal comms templates
- **Automation**: Web app testing, web artifacts builder

## Agents

### Primary Agents

- **OpenAgent**: Universal agent for questions, tasks, and workflow coordination
- **OpEncoder**: Specialized coding agent
- **Orchestrator**: Manages multi-agent workflows
- **Worker**: Executes individual tasks

### Subagents

- **Build Agent**: Type checking and build validation
- **Codebase Pattern Analyst**: Analyzes code patterns
- **Coder Agent**: Executes coding tasks
- **Reviewer**: Code review specialist
- **Tester**: Test authoring and TDD agent
- **Task Manager**: Complex feature breakdown

## Context Standards

The configuration enforces project standards through context files:

- **Code Standards**: Consistent patterns, architecture guidelines
- **Docs Standards**: Tone, structure, formatting requirements
- **Tests Standards**: Testing frameworks, coverage requirements
- **Workflows**: Review process, delegation protocols, session management

## Usage

### Basic Usage

OpenCode automatically loads this configuration on startup. Use the available commands and agents through the CLI interface.

### Customizing Agents

Edit agent definitions in `agent/` directory to modify behavior, tools, and permissions.

### Adding Skills

Create new skills in `skills/` directory following the existing pattern:
- Add a `SKILL.md` file with metadata
- Include necessary scripts and references
- Follow the skill creator guidelines in `skills/skill-creator/`

## Development

### Testing Changes

Test configuration changes without affecting production:
1. Make changes in a test branch
2. Use `/context` to verify patterns
3. Run `/test` to validate workflows

### Contributing

To add new agents, commands, or skills:
1. Follow existing patterns in respective directories
2. Include comprehensive documentation
3. Test thoroughly before submitting

## License

This configuration follows the OpenCode project license.

## Support

For issues or questions about this configuration, please refer to the OpenCode documentation or create an issue in the repository.
