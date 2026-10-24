# Security policy

## Supported versions

This repo is the canon for [Orrery](https://github.com/rfsbraz/orrery). It ships
from `main`, and there are no release branches.

| Version | Supported |
|---|---|
| `main` | yes |
| anything older | no |

## Reporting a vulnerability

**Please do not open a public issue for a security problem.**

Use [GitHub Security Advisories](https://github.com/rfsbraz/orrery-content/security/advisories/new)
to report privately. If that is unavailable to you, email rfsbraz@gmail.com with
"orrery-content security" in the subject.

Expect a first response within 7 days. If the report is valid you will be kept
updated until it is fixed, and credited in the advisory unless you would rather
not be.

## What is in scope

The content is plain YAML and images, read by the app at build time. Things
worth reporting:

- A GitHub Actions workflow in this repo that can leak a secret or run code
  from an untrusted pull request with write access.
- Injection in the scripts under `scripts/`, for example through a crafted
  YAML file or image that a curator or a workflow then processes.
- Content that, once built into the app, runs script in a reader's browser.
- A secret or personal data committed to the repo.

Problems in the app itself (accounts, Row Level Security, the site) belong to
[Orrery's security policy](https://github.com/rfsbraz/orrery/security/policy).

## What is not in scope

- The content itself being wrong. That is a curation issue, not a security one:
  open a normal issue here.
- Anything that needs write access to this repo to begin with.
