# LogLens

An offline Python log analyzer that groups recurring errors and generates a self-contained HTML health report.

LogLens turns supported application logs into severity counts, service totals, a UTC error timeline and recurring error groups. Invalid records are counted and reported instead of silently discarded.


## Quick start

Requires Python 3.11 or later. No pip packages or online services are needed.

From the extracted LogLens folder:

```text
python -m loglens samples/application.log reports normalized
```

Open `reports/report.html`. The sample contains **61 valid records, 10 error or critical events and 1 malformed record**. `reports/summary.json` contains the same analysis for scripts. A generated sample is already available at `samples/output/report.html`.

Use `python3` if that is your system's Python command.

## Analyze your own log

```text
python -m loglens path/to/application.log reports
```

The optional third argument is `exact` (default) or `normalized`. Exact mode groups identical messages within the same service and severity. Normalized mode replaces UUIDs and numeric tokens with placeholders, which can combine related messages with changing IDs. This is a heuristic and may also group unrelated events.

Outputs overwrite `report.html` and `summary.json` in the chosen directory. The tool refuses to overwrite the input with either output file.

## Supported formats

Text records:

```text
2026-01-15T09:00:00Z INFO checkout Request completed
2026-01-15T11:01:00+02:00 ERROR payments Gateway timeout for request 104
```

JSON Lines records:

```json
{"timestamp":"2026-01-15T09:00:00Z","level":"ERROR","service":"payments","message":"Gateway timeout"}
```

Every record needs timestamp, level, service and message. Text format uses a single-token service name. Timestamps require an explicit timezone; they are normalized to UTC using Python's datetime facilities (Python Software Foundation, n.d.). Supported levels are DEBUG, INFO, WARNING, ERROR and CRITICAL. WARN and FATAL are accepted aliases.

Blank lines are ignored. Bad records are skipped with a count and the first 20 affected line numbers. Input must be UTF-8. File size is limited to 50 MiB; lines longer than 65,536 characters are skipped.

## Report contents

* Parsed records, error totals, error rate and skipped records.
* One bar per UTC minute containing ERROR or CRITICAL events.
* Error groups ordered by frequency, with deterministic tie ordering.
* Severity and service distributions.
* Time range and malformed line numbers.

ERROR and CRITICAL contribute to the error rate; WARNING does not. This measures the proportion of log records, not the proportion of user requests that failed. Minutes without errors are omitted from the chart.

## Tests

```text
python -m unittest discover -s tests -v
```

See `docs/VERIFICATION.md` for recorded results. Tests cover timezone conversion, malformed input, grouping, ordering, escaping, CLI output and protection of source files.

| Exit code | Meaning |
| --- | --- |
| 0 | At least one valid record was analyzed |
| 1 | No valid records were found; diagnostic report still created |
| 2 | Invalid arguments or file processing failure |

## Structure

* `loglens/core.py`: parsing, normalization and aggregation.
* `loglens/report.py`: escaped standalone HTML.
* `loglens/__main__.py`: CLI, limits and output.
* `tests/`: standard-library unittest suite.
* `samples/`: synthetic input and generated report.

## Limits and privacy

Only the two documented formats are supported. Multiline stack traces are not joined; continuation lines count as malformed. Memory use grows with the number of unique error groups and minute buckets. This is a bounded-file diagnostic tool, not a live observability system. Reports contain log messages; review sensitive contents before sharing. No data leaves the computer during analysis.

## References

Python Software Foundation (n.d.) *datetime: Basic date and time types*. Available at: https://docs.python.org/3/library/datetime.html (Accessed: 21 October 2026).

## Licence

MIT. See LICENSE.
