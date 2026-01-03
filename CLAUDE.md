# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

This is a new/template repository. Structure and build commands will be added as the project develops.

## Security Requirements

This project uses Snyk for security scanning. When writing code:

1. Run `snyk_code_scan` tool for any new first-party code in Snyk-supported languages
2. Fix any security issues found using Snyk's context
3. Rescan after fixes to verify issues are resolved and no new issues introduced
4. Repeat until no issues remain
