# Released data

## Included figure and table inputs

`non-confidential/aggregate_main/` contains the main-figure inputs. `non-confidential/aggregate_supplementary/` contains the Supplementary Figure and Table inputs. These files are included in the Git source tree and are used by `code/run_public.py`.

See the [output index](../OUTPUT_INDEX.md) for file mappings and [data availability statement](../DATA_AVAILABILITY.md) for sources and access conditions.

## Separate county dataset download

Download [County_Inputs.zip](https://github.com/ShunlinJIN/Climate-solar-rooftop-adoption/releases/download/data-20261031/County_Inputs.zip) from [Release `data-20261031`](https://github.com/ShunlinJIN/Climate-solar-rooftop-adoption/releases/tag/data-20261031). It contains the processed daily, monthly and hourly county supporting datasets. The archive is a Release attachment; it is not included in GitHub's automatic source-code ZIP or in an anonymous mirror of the Git file tree.

Extract it **into the repository root**, the directory containing `code/` and `data/`. The archive already includes the `data/county_inputs/` directory. After extraction the three files are:

| File relative to the repository root | Contents |
| --- | --- |
| `data/county_inputs/county_daily.parquet` | Processed daily county inputs |
| `data/county_inputs/county_monthly.parquet` | Processed monthly county inputs |
| `data/county_inputs/county_hourly.parquet` | Processed hourly county inputs |

The default figure-and-table workflow uses the included aggregate inputs and does not require this additional download. These supporting county files do not replace any restricted records required by particular estimation scripts. See the [regression documentation](../code/regression/README.md).

`data/county_inputs/` is intentionally excluded from ordinary Git tracking. Data licenses and third-party access conditions are described in [DATA_LICENSE.md](../DATA_LICENSE.md) and [DATA_AVAILABILITY.md](../DATA_AVAILABILITY.md).
