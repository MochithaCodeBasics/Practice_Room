---
name: package-dependency-check
description: Check for vulnerable packages in the project
---

# Package Dependency Check Agent Skill

## Overview

This skill enables an AI agent to check for vulnerable packages in the project.

## Purpose

- Check for vulnerable packages in the project

## Inputs / Prerequisites

- If it's python project then need to install pip-audit package

```bash
pip install pip-audit
```

- If it's nodejs project then no need to install any package

## How to use this skill

- If it's python project then run below command.

```bash
pip-audit
```

- If it's nodejs project then run below command.

```bash
npm audit
```

## Troubleshooting

If you get error "command not found: pip-audit" and uv is installed then run below command.

```bash
uv add pip-audit
```

## Output

- Put the output of the package dependency check in the package_dependency_check.txt file.
