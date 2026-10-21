# Measurements

## `measurement-chart.js`

### Tooltip

When the methodology is a detection limit, the tooltip puts a sign in front of the value and does not show a methodology
line:

| Methodology (case-insensitive, trimmed) | Sign | Tooltip example |
|-----------------------------------------|------|-----------------|
| `below detection limit`                 | `<`  | `<0.5 mg/L`     |
| `at or below detection limit`           | `≤`  | `≤0.5 mg/L`     |
| `above detection limit`                 | `>`  | `>0.5 mg/L`     |
| `at or above detection limit`           | `≥`  | `≥0.5 mg/L`     |

Example:

```
● Groundwater Quality: 0.5 mg/L
```