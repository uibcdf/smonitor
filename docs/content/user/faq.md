# FAQ

## Do I need to import SMonitor in every module?

No. Configure once at package startup (`ensure_configured`).
Then use `@signal` and catalog-based emitters where needed.

## Should end users control SMonitor directly?

Usually not. Most libraries should expose sensible defaults for end users.
Developers and QA can override profile/config at runtime or via environment.

## Where should warning/error templates live?

In your catalog (`A/_private/smonitor/catalog.py`) as the single source of truth.
Avoid duplicating templates in multiple files.

## Can I keep my custom exceptions?

Yes. Inherit from `CatalogException` and map each class to `catalog_key`.
You keep class semantics while centralizing message quality.

## Is SMonitor too heavy for tight compute loops?

Instrument boundaries, not inner hot loops.
Use `@signal` in API/orchestration layers for high value with low overhead.

## What if emission fails?

Do not silence it. Emit a fallback warning/log line with context.
Silent failures destroy traceability and slow down debugging.

## Can I adopt SMonitor incrementally?

Yes, and that is recommended.
Start with one subsystem, then expand by warning/error families.

## Where is the canonical integration contract?

Use:
- [SMONITOR_GUIDE.md](https://github.com/uibcdf/smonitor/blob/main/standards/SMONITOR_GUIDE.md)
