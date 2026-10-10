# Internship Application Assistant

A Python-based assistant designed to make internship searches more efficient: discover relevant opportunities, prioritize them against a candidate's profile, and prepare applications for **manual review and submission**.

> **Project status:** Planning stage. This repository currently documents the concept; implementation has not started.

## The problem

Internship opportunities are scattered across company career pages, job boards, and university portals. Finding suitable roles, checking eligibility, tailoring application materials, and keeping track of submissions can take more time than the applications themselves.

## The idea

Build a personal internship-search workflow that handles repetitive research and preparation while keeping the applicant in control.

1. **Discover:** Periodically collect internship listings from supported, permitted sources.
2. **Filter:** Remove duplicates and screen for location, dates, field, academic level, and other eligibility requirements.
3. **Prioritize:** Compare each opportunity with a user-defined profile and explain the match, including potential gaps or uncertain requirements.
4. **Prepare:** Draft tailored CV suggestions and, when appropriate, cover-letter text based **only on verified information** from the user's profile.
5. **Review:** Send a concise daily digest through Telegram, with links to the original postings.
6. **Apply manually:** The user reviews the materials and submits applications on the employer's website.
7. **Track:** Record application status, dates, follow-ups, and deadlines.

The goal is **high-quality applications, not automated mass submissions**.

## Planned features

- Internship monitoring across multiple sources
- Deduplication and searchable vacancy history
- Custom eligibility filters and a transparent relevance score
- Telegram notifications and an evening digest
- Application preparation with human approval
- Application tracker and deadline reminders
- Optional LLM-powered vacancy summaries and CV tailoring

## Planned technology

| Component | Initial direction |
| --- | --- |
| Core | Python |
| API / backend | FastAPI |
| Telegram interface | aiogram |
| Database | SQLite |
| Data collection | Official/publicly accessible feeds and APIs where permitted |
| Ranking | Rule-based matching first; ML/LLM enhancements later |

The architecture and stack may evolve as the project develops.

## Intended audience

Initially a personal tool for a Computer Science & AI student seeking software engineering and AI/ML internships. It may later be extended to support configurable profiles for other students.

---

*This README describes planned functionality, not features that are already implemented.*
