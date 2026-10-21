# GWML2 Django Admin

This folder holds the Django admin configuration for the `gwml2` app. Each module registers one or more models.
Harvester admin lives separately in
`gwml2/harvesters/admin.py` and is imported from `__init__.py`.

This document lists every **admin action** (the "Action" dropdown on the change list) and explains what it does and when
to use it.

## How actions run

Actions run in one of three ways. Knowing which one tells you where to look for progress or errors.

| Mode                   | How it works                                                                                                                                                   | Where to check progress                                                                     |
|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| **Management command** | Uses `run_command` (`gwml2/utils/management_commands.py`) to create a GeoNode `ManagementCommandJob` and start it. You are then redirected to that job's page. | *Admin → Management command jobs* (`/admin/management_commands_http/managementcommandjob/`) |
| **Celery task**        | Queued with `.delay(...)` on the `update` queue. The page returns right away.                                                                                  | Celery logs, or the model's own status field                                                |
| **Synchronous**        | Runs inside the HTTP request. A large selection can time out.                                                                                                  | The page itself                                                                             |

Most cache commands are called with `--force`, so they **regenerate the data even if it already exists**.

---

## Wells (`well.py`)

### Well - `WellAdmin`

| Action                                  | Mode                                                     | Purpose                                                                                                                                                                                                                                                                                    |
|-----------------------------------------|----------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Download well data**                  | Synchronous (redirect)                                   | Sends the selected well IDs to the public download flow (`well_download_request_by_ids_initiate`) with data type *well and monitoring data*. This creates a `DownloadRequest`, the same as a user downloading from the frontend. Use it to get a data file for a few specific wells.       |
| **Delete selected wells in background** | Confirmation page → Celery                               | Superuser only. Shows a confirmation page with the number of wells and level/quality/yield measurements per organisation, then deletes them in the background through `WellDeletion`. Use this instead of Django's default delete, which would time out on wells with many measurements.   |
| **Assign country**                      | Synchronous                                              | Sets `Well.country` again. Uses the organisation's country if it has one; otherwise uses the country polygon that contains the well's location (`force=True`). Use it after fixing coordinates or an organisation's country.                                                               |
| **Translate description**               | Synchronous                                              | Translates `description` with DeepL and saves it. Use it for wells whose description is not in English. Calls an external API for each well, so keep the selection small.                                                                                                                  |
| **Generate DEM value**                  | Management command `generate_dem_well_value`             | Fills `glo_90m_elevation` from the Copernicus GLO-90 DEM, downloading each 1°×1° tile once. Skips wells that already have a value, have no location, or got an empty DEM result before. Afterwards it regenerates the `general_information` data cache for the updated wells.              |
| **Generate metadata**                   | Management command `generate_well_metadata`              | Recalculates the stored measurement counts (`number_of_measurements*`) and `first_time_measurement` / `last_time_measurement` from the measurement tables. Use it when the numbers in the list don't match the real data.                                                                  |
| **Generate data cache**                 | Management command `generate_data_wells_cache`           | Rebuilds the per-well download files (general information, hydrogeology, management, drilling and construction, monitoring). Then rebuilds the country and organisation zip files those wells belong to. Use it after data changes that did not go through the normal save or upload flow. |
| **Generate data cache information**     | Management command `generate_data_cache_information`     | Diagnostic only. Scans the well's cache folder and measurement cache files and stores each file name with its last modified time in `WellCacheIndicator.data_cache_information`. Does not regenerate anything; it shows what is on disk.                                                   |
| **Generate level not daily cache**      | Management command `generate_well_level_not_daily_cache` | Recalculates the `Well.is_level_not_daily` flag. It is `True` when at least two consecutive level measurements are less than 23 hours apart, which means the data is finer than daily. Used by the *is level not daily* filter.                                                            |

### Materialized view well - `MaterializedViewWellAdmin`

| Action      | Mode        | Purpose                                                                                                                                                                                              |
|-------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Refresh** | Synchronous | Runs `REFRESH MATERIALIZED VIEW mv_well`. The view feeds the map and the quality control flags. Refresh it after bulk changes so they appear. The whole view is refreshed no matter what you select. |

### Measurements (Level / Quality / Yield) - `MeasurementAdmin`

No custom actions. These are read-mostly views with extra filters (page size, organisation, date and time-of-day range,
value range).

---

## Well cache indicator (`well_cache_indicator.py`)

`WellCacheIndicatorAdmin` shows when each cache was last generated for a well. The actions run on the wells behind the
selected rows.

| Action                              | Mode                                                 | Purpose                                                                                                                                                                                                                     |
|-------------------------------------|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Generate data cache**             | Management command `generate_data_wells_cache`       | Same as *Generate data cache* on Well.                                                                                                                                                                                      |
| **Generate metadata**               | Management command `generate_well_metadata`          | Same as *Generate metadata* on Well.                                                                                                                                                                                        |
| **Generate data cache information** | Management command `generate_data_cache_information` | Same as on Well. Refreshes the *Data cache information* column.                                                                                                                                                             |
| **Generate measurement group data** | Management command `generate_measurement_group_data` | Rebuilds `WellMeasurementGroupData`: one row per well × measurement type × parameter × unit, with begin/end time and count. Used as the summary of a well's monitoring data. Updates `measurement_group_data_generated_at`. |

---

## Well quality control (`well_quality_control.py`)

`WellQualityControlAdmin` shows the groundwater level quality checks for each well. The thresholds are set in **Site
preference**.

| Action                   | Mode                                                      | Purpose                                                                                                                                                                                                                            |
|--------------------------|-----------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Force generate**       | Management command `generate_well_quality_control`        | Clears the generated timestamps and runs the checks again: **time gap**, **value gap** and **strange value**. Then refreshes `mv_well` so the map shows the new flags. Use it after changing the thresholds or the measurements.   |
| **Clean duplicate well** | Management command `clean_well_quality_control_duplicate` | Database cleanup. Deletes `WellQualityControl` rows whose well no longer exists. For wells with more than one row, deletes them all and creates one new row, then runs it. **Works on the whole table; the selection is ignored.** |

---

## Organisation (`organisation.py`)

### Organisation - `OrganisationAdmin`

| Action                        | Mode                                                       | Purpose                                                                                                                                                                                                                                                   |
|-------------------------------|------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Generate data wells cache** | Management command `generate_data_organisations_cache`     | Rebuilds the organisation's download zip from the existing per-well cache files. Does not rebuild the per-well files; use *Generate data cache* on Well for that.                                                                                         |
| **Reassign wells country**    | Synchronous                                                | Sets the country of all wells in the organisation to the organisation's country. Organisations without a country are skipped. Use it after setting or changing an organisation's country.                                                                 |
| **Update ggis uid of wells**  | Celery (`update_ggis_uid`)                                 | Recalculates `ggis_uid` (`<organisation name>-<original_id>`) for all the organisation's wells, in batches of 10,000. Use it after renaming an organisation.                                                                                              |
| **Generate metadata cache**   | Management command `generate_organisations_metadata_cache` | Updates `data_cache_generated_at` from the zip file's modified time. Recalculates `data_date_start` / `data_date_end`, `data_is_from_api` (true when a harvester exists) and `data_stats`, the numbers in the *Measurement Stats* / *Well Stats* columns. |

### Organisation group / Organisation type

No custom actions.

---

## Country (`general.py`)

`CountryAdmin`.

| Action                      | Mode                                                   | Purpose                                                                                                                                                                                                         |
|-----------------------------|--------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Generate data cache**     | Management command `generate_data_countries_cache`     | Rebuilds the country download zips (`<code>.zip` and `<code>-ggmn.zip`) from the per-well cache files.                                                                                                          |
| **Generate metadata cache** | Management command `generate_countries_metadata_cache` | Updates `data_cache_generated_at` from the zip file's modified time. Recalculates the statistics for the **Groundwater Observations Repository** (active organisations not in the GGMN group) and for **GGMN**. |

`Unit`, `UnitGroup` and `Quantity` have no custom actions.

---

## Site preference (`site_preference.py`)

`SitePreferenceAdmin` holds global settings. Its actions do **not** depend on the selected row; select the single
preference row and run.

| Action                                                           | Mode                              | Purpose                                                                                                                                                                                                                                      |
|------------------------------------------------------------------|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Update running harvesters**                                    | Synchronous                       | Syncs the `running_harvesters` list with the harvesters that are really running in Celery. Use it when a harvester shows *RUNNING* but has stopped (for example after a worker restart).                                                     |
| **Running all harvesters**                                       | Synchronous (starts Celery tasks) | Same as the scheduled `run_all_harvester` job. Fills the free slots (`running_harvesters_concurrency_count` minus running) with the next active harvesters. Skips harvesters that are running or finished successfully in the last 24 hours. |
| **Clean dangling measurement cache**                             | Celery                            | Deletes files and folders in `MEASUREMENTS_FOLDER` that belong to wells which no longer exist. Frees disk space after deletions.                                                                                                             |
| **Clean dangling well data cache**                               | Celery                            | Same, for `GWML2_FOLDER/wells-data` (per-well download files).                                                                                                                                                                               |
| **Generate organisation/country/quality control metadata cache** | Celery                            | Runs `generate_organisations_metadata_cache` and then `generate_countries_metadata_cache` for **all** records, so dashboard statistics stay current. Uses a file lock, so two runs cannot overlap.                                           |

---

## Upload session (`upload_session.py`)

`UploadSessionAdmin` manages batch well and monitoring uploads.

| Action                                   | Mode        | Purpose                                                                                                                                                               |
|------------------------------------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Stop upload.**                         | Synchronous | Cancels the Celery task (`terminate=True`) and sets `is_canceled`.                                                                                                    |
| **Resume upload.**                       | Celery      | Clears `is_canceled` and runs the upload again, continuing from the last checkpoint. Does nothing if the task is still running.                                       |
| **Restart upload.**                      | Celery      | Clears `is_canceled` and runs the upload from the beginning (`restart=True`).                                                                                         |
| **Create report.**                       | Celery      | Creates the Excel report again, with rows marked Added / Error / Skipped, from the stored `UploadSessionRowStatus`. Use it when the report is missing or out of date. |
| **Clean row status.**                    | Synchronous | Deletes all `UploadSessionRowStatus` rows of the session to save database space. **After this the report cannot be created again**, so create it first.               |
| **Delete uploaded file (space saving).** | Synchronous | Deletes the uploaded source file from storage. Sessions newer than 1 week are skipped with a warning.                                                                 |
| **Delete report file (space saving).**   | Synchronous | Deletes the generated report file(s). Same 1 week rule.                                                                                                               |

The **Running uploader** filter shows sessions that are not processed, not canceled and below 100% progress.

`UploadSessionRowStatusAdmin` has no custom actions.

---

## Well deletion (`well_deletion.py`)

`WellDeletionAdmin` tracks background deletions started by *Delete selected wells in background*.

| Action  | Mode                         | Purpose                                                                           |
|---------|------------------------------|-----------------------------------------------------------------------------------|
| **Run** | Celery (`run_well_deletion`) | Runs the deletion job again. Use it when a deletion stopped before reaching 100%. |

---

## Download request (`download_request.py`)

`DownloadRequestAdmin`.

| Action                   | Mode        | Purpose                                                                                                                                                                                                                                                       |
|--------------------------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Run download request** | Synchronous | Builds the download file for the request again (`DownloadRequest.run`). Use it when a request failed (`is_error`) or is stuck. **It runs inside the HTTP request**, not in Celery, so large requests may time out. Fails early if free disk space is too low. |

---

## Harvester (`gwml2/harvesters/admin.py`)

`HarvesterAdmin`.

| Action  | Mode                     | Purpose                                                                                                                                                                           |
|---------|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Run** | Celery (`run_harvester`) | Starts the selected harvesters now. Harvesters that are already running are skipped. Each run writes a `HarvesterLog`; its *Well Progress* CSV can be downloaded from the inline. |

---

## Models without custom actions

These use the default admin (CRUD, sometimes with inlines or `raw_id_fields`):

- `construction.py`: `Construction` (inline `ConstructionStructure`)
- `drilling.py`: `Drilling` (inlines `StratigraphicLog`, `WaterStrike`)
- `geology.py`: `Geology`
- `hydrogeologic_parameters.py`: `HydrogeologyParameter`, `PumpingTest`
- `management.py`: `Management`, `License`
- `reference_elevation.py`: `ReferenceElevation`
- `form_help_text.py`: `FormHelpText` (help text shown on the well form)
- `term.py`: the `Term*` vocabularies and `TermMeasurementParameter` / `TermMeasurementParameterGroup`
- `well_measurement_group_data.py`: `WellMeasurementGroupData` (read-only; filled by *Generate measurement group data*)
- `well.py`: `WellDocument`
