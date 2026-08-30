# Data Availability

## Publicly released replication data

This repository includes the non-identifying source data required by the public
reproduction workflow:

```text
data/non-confidential/aggregate_main/
data/non-confidential/aggregate_supplementary/
```

These released files are sufficient to regenerate all displayed main figures,
Supplementary Figures, and Supplementary Tables.

## Restricted source records

Some upstream analyses use administrative rooftop-PV installation records,
household electricity-flow records, hourly household telemetry, or
household-level survey records that cannot be openly redistributed because of
data-use, confidentiality, privacy, or third-party redistribution restrictions.

Those restricted source records are not included in the public repository.
Access requires authorization from the relevant data holder and compliance with
the applicable data-use, confidentiality, ethical, privacy, and legal
requirements.

Because those source records are not publicly redistributable, upstream code
that depends exclusively on those unavailable inputs is not included in the
public reproduction package.

## External data sources

Meteorological observations are obtained from the China Meteorological Data
Service Center. Near-term adoption projections use NEX-GDDP-CMIP6 climate
products. Other environmental, socioeconomic, and policy data sources are
described in the manuscript and Supplementary Information and remain subject to
their original access and redistribution terms.

## Scope of the public package

The public package is designed for exact reproduction of displayed outputs from
the released non-confidential source-data layer. It does not claim to
reconstruct or redistribute restricted source records.
