# Design notes

Parsing produces an immutable Entry with a UTC timestamp. JSON Lines and text input share the same validation stage, so aggregation does not depend on the input format.

The analyzer walks the file once, retaining counters rather than every parsed row. Counts are keyed by severity, service and UTC minute. Error groups include service and severity to keep similar messages from different components separate. Time bounds use minimum and maximum timestamps, so out-of-order input is handled correctly.

Exact grouping is the default because replacing all numbers can erase meaningful differences. Normalized grouping is an explicit option; the report states that it is heuristic. UUIDs are replaced before numeric tokens to preserve a useful placeholder.

HTML escaping is applied to log-derived values. Summary JSON remains structured data and does not depend on HTML parsing. The report uses no JavaScript or external assets.

The 50 MiB CLI input limit bounds ordinary file size, but grouping memory still depends on cardinality. Streaming from a pipe, multiline parsing, log-format adapters and bounded top-k aggregation are future extensions, not implemented features.
