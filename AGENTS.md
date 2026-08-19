# Project Instructions

## Protected Files

The following files and directories are PROTECTED:

- `expense_tracker.db`
- `.env`
- `migrations/`
- `README.md`

## Strict Protection Rules

NEVER delete, remove, truncate, overwrite, reset, or modify these protected files or directories.

This applies to ALL methods, including:

- `rm`
- `rm -rf`
- `del`
- `Remove-Item`
- `unlink`
- `truncate`
- Python scripts
- PowerShell commands
- shell commands
- SQL commands
- Git commands
- Any other command or tool

NEVER execute a command that could delete or modify a protected file.

If the user explicitly asks you to delete, reset, overwrite, or modify a protected file, DO NOT perform the operation automatically.

Instead, STOP and ask the user for explicit confirmation before doing anything.

## Database Protection

`expense_tracker.db` contains project data.

NEVER:

- Delete the database
- Drop the database
- Truncate database files
- Replace the database
- Reset the database
- Run destructive database operations without explicit user confirmation

If a command might affect `expense_tracker.db`, STOP and ask for confirmation.

## Environment Protection

NEVER delete or overwrite `.env`.

Never expose or print secrets contained in `.env`.

## Migration Protection

NEVER delete or modify the `migrations/` directory unless the user explicitly confirms the exact operation.

## README Protection

NEVER delete `README.md`.

Do not overwrite the README unless the user explicitly asks for a specific change.

## Before Destructive Operations

Before performing ANY destructive operation:

1. Identify exactly what will be changed or deleted.
2. Check whether it affects a protected file.
3. If it affects a protected file, STOP.
4. Ask the user for explicit confirmation.
5. Do not execute the command until confirmation is received.

## General Rule

When there is uncertainty about whether an operation could affect a protected file, DO NOT execute it.

Ask the user first.
