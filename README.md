# AgentCore DevOps Assistant

Slack-integrated DevOps/Task management assistant demo showcasing AgentCore Gateway, Runtime, and Memory.

## Overview

**Purpose:** Full showcase of AgentCore capabilities (Gateway, Runtime, Memory, Interceptors)

**Target Audience:** AWS developers, Solution Architects, Presales

## Architecture

```
[Slack User]
    ↓
[EKS Pod: Slack Bot + Strands Agent]
    ↓
[AgentCore Gateway]
    ↓
[Request Interceptor Lambda]
    ↓
┌───┴────┬──────────┬──────────┬──────────┐
↓        ↓          ↓          ↓          ↓
Slack    Task API   DuckDuckGo AWS API    DeepWiki
Webhook  REST API   Lambda     MCP Runtime MCP Server
```

## Key Features

### 4 Target Types Integration

1. **OpenAPI Target** - Slack Webhook, Task REST API
2. **Lambda Target** - DuckDuckGo search
3. **MCP Server Target** - AWS API (AgentCore Runtime), DeepWiki MCP (Remote)
4. **Gateway Interceptors** - Unified schema transformation

### Available Tools

- **Web Search**: DuckDuckGo search
- **Slack Notification**: Incoming Webhook
- **Task Management**: Create, list, delete tasks
- **Infrastructure Health Check**: 15,000+ AWS APIs via AWS CLI (CloudFront, S3, API Gateway, Lambda, DynamoDB, etc.)
- **Project Self-Explanation**: Read codebase from S3 and explain architecture, implementation, deployment

## Quick Start

### Prerequisites

- AWS CLI configured
- Python 3.11+
- eksctl, kubectl
- Finch or Docker
- Slack App (Bot Token, App Token, Webhook URL)

### Deployment

```bash
# Step 1: Foundation resources (5 min)
./scripts/deploy_step1_foundation.sh

# Step 2: Interceptor (2 min)
./scripts/deploy_step2_interceptor.sh

# Step 2.5: Task API setup (5 min)
./scripts/deploy_step2_5_task_api.sh

# Step 3: Gateway Targets (10 min)
./scripts/deploy_step3_targets.sh

# Step 4: EKS deployment (20 min)
./scripts/deploy_step4_eks.sh
```

**Total time: ~40 minutes**

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for details.

## Usage

### Slack Commands

```
@bot Check task app status
@bot Create a deployment task for tomorrow
@bot Search for Kubernetes 1.32 new features
@bot Explain this project structure
@bot Explain Strands Agent implementation
```

## Project Structure

```
.
├── slack_bot/              # Slack Bot (Socket Mode)
├── strands_agent/          # Strands Agent (TaskBot)
│   ├── agent.py            # Main agent implementation
│   ├── tools/              # Gateway tool integration
│   └── hooks/              # Memory hook integration
├── k8s/                    # Kubernetes manifests
├── scripts/                # Deployment scripts
├── config/                 # Configuration files (auto-generated)
└── docs/                   # Documentation
```

## Tech Stack

- **Agent Framework**: Strands Agents
- **AgentCore**: Gateway, Runtime, Memory, Interceptors
- **Backend**: Lambda, API Gateway, DynamoDB
- **Frontend**: React, CloudFront, S3
- **Infrastructure**: EKS, ECR
- **Container**: Finch/Docker

## Documentation

- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Deployment guide
- [docs/DEMO_SCENARIO.md](docs/DEMO_SCENARIO.md) - Demo scenarios
- [.kiro/steering/design.md](.kiro/steering/design.md) - Architecture design

## License

MIT
