---
name: static-analysis
description: Static analysis of code using semgrep
---

# Semgrep Agent Skill

## Overview

This skill enables an AI agent to run Semgrep for static code analysis and security scanning.
It detects vulnerabilities, insecure coding patterns, misconfigurations, and compliance issues in source code.

Semgrep is lightweight, fast, and supports multiple languages including Python, JavaScript, TypeScript, Java, Go, Ruby, and more.

## Purpose

- Run Semgrep for static code analysis and security scanning
- Detect vulnerabilities, insecure coding patterns, misconfigurations, and compliance issues in source code
- Support multiple languages including Python, JavaScript, TypeScript, Java, Go, Ruby, and more

## Inputs / Prerequisites

- Docker must be installed on the system. If not present then run below command.

## When to use this skill

Use this skill when you are going to scan the code for vulnerabilities, insecure coding patterns, misconfigurations, and compliance issues in source code.

## How to use this skill

```bash
docker run --rm -v .:/src semgrep/semgrep semgrep scan --config auto /src
```

## Output

Please put the output of the semgrep scan in the semgrep_report.txt file.