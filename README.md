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

3. Set up environment variables:
   - Copy the example environment file: `cp .env.example .env`
   - Edit `.env` with your API keys
   - The `CONTEXT7_API_KEY` is required for documentation search

## Configuration

### Environment Variables

Create a `.env` file in the root directory (excluded from git):

```env
# Context7 API key for documentation search (required)
CONTEXT7_API_KEY=your_context7_api_key_here
```

### Main Config Files

- **`opencode.json`**: Main OpenCode configuration (MCP servers, models, plugins, providers)
- **`oh-my-opencode.json`**: OhMyOpenCode plugin settings
- **`dcp.jsonc`**: DCP plugin configuration
- **`package.json`**: Node.js dependencies and scripts

## Structure

```
.
├── agent/                    # AI agent definitions
│   ├── openagent.md        # Universal primary agent
│   ├── opencoder.md        # Coding specialist
│   ├── orchestrator.md     # Workflow coordinator
│   ├── reviewer.md         # Code review specialist
│   ├── worker.md           # Task execution agent
│   └── subagents/          # Specialized subagents
│       ├── code/           # Code-focused subagents
│       │   ├── build-agent.md
│       │   ├── codebase-pattern-analyst.md
│       │   ├── coder-agent.md
│       │   ├── reviewer.md
│       │   └── tester.md
│       ├── core/           # Core workflow subagents
│       │   ├── documentation.md
│       │   └── task-manager.md
│       ├── gtk-ui-ux-engineer.md
│       └── python-engineer.md
├── command/                  # Slash commands
│   ├── background.md        # Background job management
│   ├── commit.md            # Commit workflow
│   ├── context.md           # Project analysis
│   ├── deploy.md            # Deployment with Kamal
│   ├── graphite.md          # Graphite CLI integration
│   ├── optimize.md           # Code analysis
│   ├── plan.md              # Rails feature planning
│   ├── rmslop.md            # Remove AI-generated code
│   ├── swarm.md             # Multi-agent orchestration
│   ├── swarm-abort.md       # Abort swarm workflow
│   ├── swarm-status.md      # Check swarm status
│   └── test.md              # Testing pipeline
├── context/                  # Standards and workflows
│   ├── core/
│   │   ├── essential-patterns.md
│   │   ├── standards/       # Code, docs, tests standards
│   │   ├── system/          # System documentation
│   │   └── workflows/       # Review, delegation workflows
│   └── project/
│       └── project-context.md
├── skills/                   # Reusable skill modules
│   ├── algorithmic-art/
│   ├── brand-guidelines/
│   ├── canvas-design/
│   ├── doc-coauthoring/
│   ├── docx/
│   ├── frontend-design/
│   ├── gtk-ui-ux-engineer/
│   ├── internal-comms/
│   ├── mcp-builder/
│   ├── pdf/
│   ├── pptx/
│   ├── python-engineer/
│   ├── rails-basecamp-engineer/
│   ├── self-learning/
│   ├── skill-creator/
│   ├── slack-gif-creator/
│   ├── theme-factory/
│   ├── webapp-testing/
│   ├── web-artifacts-builder/
│   └── xlsx/
├── opencode.json            # Main config
├── oh-my-opencode.json      # OhMyOpenCode plugin
├── dcp.jsonc                # DCP plugin config
├── package.json             # Node.js dependencies
├── .env                     # Environment variables (not in git)
├── .env.example             # Example environment file
├── .gitignore               # Git exclusions
└── README.md                # This file
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/background` | Check history and status of current/latest background jobs |
| `/commit` | Create conventional commits with emoji |
| `/context` | Analyze project structure and patterns |
| `/deploy` | Deploy using Kamal (async) |
| `/graphite` | Use Graphite CLI to create, stack and submit pull requests |
| `/optimize` | Code performance and security analysis |
| `/plan` | Plan Rails features with multi-tenant architecture |
| `/rmslop` | Remove AI-generated code slop |
| `/swarm` | Start multi-agent workflow |
| `/swarm-abort` | Abort current swarm and revert all changes |
| `/swarm-status` | Check status of current swarm session |
| `/test` | Run complete Rails testing pipeline |

## MCP Servers

The configuration connects to several MCP servers:

- **Context7**: Documentation search and code examples (enabled)
- **Chrome DevTools**: Browser automation and testing (enabled)
- **Tiger PostgreSQL (pg-aiguide)**: Database documentation and guidance for TimescaleDB/Tiger Cloud (enabled)
- **Playwright**: Browser automation (disabled)
- **Tidewave**: Custom server (disabled)

## Skills

This config includes 19 skills for specialized tasks:

### Document Processing
- **DOCX**: Word document processing and manipulation
- **PPTX**: PowerPoint operations and creation
- **PDF**: PDF manipulation and processing
- **XLSX**: Excel spreadsheet operations

### Design & UI/UX
- **Algorithmic Art**: Generative art and creative coding
- **Canvas Design**: Visual design workflows
- **Frontend Design**: UI/UX patterns and best practices
- **GTK UI/UX Engineer**: Native Linux desktop application design
- **Theme Factory**: Theme generation and management

### Development
- **Rails Basecamp Engineer**: Ruby on Rails development patterns
- **Python Engineer**: Python development and best practices
- **MCP Builder**: Building Model Context Protocol servers

### Communication
- **Internal Comms**: Internal communication templates and examples
- **Doc Coauthoring**: Document collaboration workflows

### Automation & Testing
- **Web App Testing**: Browser-based application testing
- **Web Artifacts Builder**: Building web-based artifacts

### Utilities
- **Brand Guidelines**: Brand consistency and guidelines
- **Self-Learning**: Learning and knowledge management
- **Skill Creator**: Creating new OpenCode skills
- **Slack GIF Creator**: Creating GIFs for Slack communication

## Agents

### Primary Agents

- **OpenAgent**: Universal agent for questions, tasks, and workflow coordination
- **OpEncoder**: Specialized coding agent
- **Orchestrator**: Manages multi-agent workflows
- **Reviewer**: Code review specialist
- **Worker**: Executes individual tasks

### Subagents

#### Code Subagents
- **Build Agent**: Type checking and build validation
- **Codebase Pattern Analyst**: Analyzes code patterns
- **Coder Agent**: Executes coding tasks
- **Reviewer**: Code review specialist (also primary agent)
- **Tester**: Test authoring and TDD agent

#### Core Subagents
- **Documentation**: Technical documentation authoring
- **Task Manager**: Complex feature breakdown and task coordination

#### Specialist Subagents
- **GTK UI/UX Engineer**: Native Linux desktop application design
- **Python Engineer**: Expert Python development with modern best practices

## Context Standards

The configuration enforces project standards through context files:

### Core Standards
- **Code Standards**: Consistent patterns, architecture guidelines
- **Docs Standards**: Tone, structure, formatting requirements
- **Tests Standards**: Testing frameworks, coverage requirements
- **Analysis Standards**: Code analysis and evaluation patterns
- **Patterns Standards**: Architectural and design patterns

### Core Workflows
- **Review Workflow**: Code review process and standards
- **Delegation Workflow**: Agent delegation protocols
- **Sessions Workflow**: Session management best practices
- **Task Breakdown Workflow**: Complex task decomposition
- **Context Guide**: System context management

### Project Context
- **Project Context**: Project-specific configuration and standards

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
