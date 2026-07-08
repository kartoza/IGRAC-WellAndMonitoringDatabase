(function ($) {
  let allOrganisations = [];
  let allCountries = [];
  let selectedCountries = [];
  let lengthOfTimeSeriesChart = null;
  let numberOfStationsChart = null;
  let selectedDashboardNumberStations = 1;

  let ANIMATION_DURATION = 500;
  let RECENTLY_UPDATED_YEARS = 2;

  let COUNTRY_STAT_FIELDS = [
    'count_well', 'count_well_with_level', 'count_well_with_quality',
    'count_spring', 'count_measurement_level', 'count_measurement_quality'
  ];

  function computeStats(organisations) {
    let totals = {
      count_organisation: organisations.length,
      count_automatic_connection: 0
    };
    $.each(organisations, function (index, organisation) {
      if (organisation.data_is_from_api) {
        totals.count_automatic_connection += 1;
      }
    });
    return totals;
  }

  function combineCountryFieldStats(a, b) {
    let combined = {};
    $.each(COUNTRY_STAT_FIELDS, function (index, field) {
      combined[field] = (a[field] || 0) + (b[field] || 0);
    });
    let starts = [a.data_date_start, b.data_date_start].filter(Boolean);
    let ends = [a.data_date_end, b.data_date_end].filter(Boolean);
    combined.data_date_start = starts.length ? starts.reduce(
      function (min, d) {
        return new Date(d) < new Date(min) ? d : min;
      }
    ) : null;
    combined.data_date_end = ends.length ? ends.reduce(
      function (max, d) {
        return new Date(d) > new Date(max) ? d : max;
      }
    ) : null;
    return combined;
  }

  function countryStats(country, showGGMN, showObservationsRepository) {
    let repository = country.statistic_observations_repository || {};
    let ggmn = country.statistic_ggmn || {};

    if (showGGMN && showObservationsRepository) {
      return combineCountryFieldStats(repository, ggmn);
    }
    if (showGGMN) {
      return ggmn;
    }
    if (showObservationsRepository) {
      return repository;
    }
    return null;
  }

  function isRecentlyUpdated(dateEnd) {
    if (!dateEnd) {
      return false;
    }
    let threshold = new Date();
    threshold.setFullYear(
      threshold.getFullYear() - RECENTLY_UPDATED_YEARS
    );
    return new Date(dateEnd) >= threshold;
  }

  function computeCountryStats(countries, showGGMN, showObservationsRepository) {
    let totals = {
      count_country: 0,
      count_country_recently_updated: 0
    };
    $.each(COUNTRY_STAT_FIELDS, function (index, field) {
      totals[field] = 0;
    });
    $.each(countries, function (index, country) {
      let stats = countryStats(
        country, showGGMN, showObservationsRepository
      );
      if (!stats || (stats.count_well || 0) <= 0) {
        return;
      }
      totals.count_country += 1;
      if (isRecentlyUpdated(stats.data_date_end)) {
        totals.count_country_recently_updated += 1;
      }
      $.each(COUNTRY_STAT_FIELDS, function (index, field) {
        totals[field] += stats[field] || 0;
      });
    });
    return totals;
  }

  function isCountryOrganisationVisible(organisation) {
    if (!organisation.country_id) {
      // No country assigned: treat the organisation as belonging to
      // every country, so it stays visible as long as at least one
      // country is selected.
      return selectedCountries.length > 0;
    }
    return selectedCountries.indexOf(String(organisation.country_id)) !== -1;
  }

  function getActiveDataTypes() {
    let filters = [];
    $('#dashboard-data-type .dashboard-toggle.active').each(function () {
      filters.push($(this).data('type'));
    });
    return {
      showGGMN: filters.indexOf('ggmn') !== -1,
      showObservationsRepository: filters.indexOf('observations_repository') !== -1
    };
  }

  function filterOrganisations(organisations, showGGMN, showObservationsRepository) {
    return $.grep(organisations, function (organisation) {
      if (!isCountryOrganisationVisible(organisation)) {
        return false;
      }
      if (organisation.is_ggmn) {
        return showGGMN;
      }
      return showObservationsRepository;
    });
  }

  function filterCountries(countries) {
    return $.grep(countries, function (country) {
      return selectedCountries.indexOf(String(country.id)) !== -1;
    });
  }

  function renderStats() {
    let dataType = getActiveDataTypes();
    let showGGMN = dataType.showGGMN;
    let showObservationsRepository = dataType.showObservationsRepository;

    let filtered = filterOrganisations(
      allOrganisations, showGGMN, showObservationsRepository
    );
    let totals = computeStats(filtered);
    $.extend(
      totals,
      computeCountryStats(
        filterCountries(allCountries), showGGMN, showObservationsRepository
      )
    );
    $.each(totals, function (key, value) {
      let $cell = $('[data-stat="' + key + '"]');
      let from = WellDashboardUtils.parseNumber($cell.text());
      let to = Number(value) || 0;
      WellDashboardUtils.animateStat($cell, from, to, ANIMATION_DURATION);
    });

    renderLengthOfTimeSeriesChart();
    renderNumberOfStationsChart();
  }

  function getThemeColors() {
    return {
      primary: getComputedStyle(document.documentElement)
        .getPropertyValue('--dashboard-color-primary').trim(),
      secondary: getComputedStyle(document.documentElement)
        .getPropertyValue('--dashboard-color-accent').trim()
    };
  }

  function renderLengthOfTimeSeriesChart() {
    let dataType = getActiveDataTypes();
    let showGGMN = dataType.showGGMN;
    let showObservationsRepository = dataType.showObservationsRepository;

    let countries = filterCountries(allCountries).slice().sort(
      function (a, b) {
        return a.name.localeCompare(b.name);
      }
    );

    let themeColors = getThemeColors();
    let primaryColor = themeColors.primary;
    let secondaryColor = themeColors.secondary;

    let categories = [];
    let data = [];
    $.each(countries, function (index, country) {
      let stats = countryStats(
        country, showGGMN, showObservationsRepository
      );
      if (!stats || !stats.data_date_start || !stats.data_date_end) {
        return;
      }
      let isOdd = categories.length % 2 === 0;
      categories.push(country.name);
      data.push({
        low: new Date(stats.data_date_start).getTime(),
        high: new Date(stats.data_date_end).getTime(),
        color: isOdd ? primaryColor : secondaryColor
      });
    });

    $('#dashboard-length-of-time-series-loading').addClass('hidden');

    if (!categories.length) {
      if (lengthOfTimeSeriesChart) {
        lengthOfTimeSeriesChart.destroy();
        lengthOfTimeSeriesChart = null;
      }
      $('#dashboard-length-of-time-series-empty').removeClass('hidden');
      return;
    }
    $('#dashboard-length-of-time-series-empty').addClass('hidden');

    lengthOfTimeSeriesChart = Highcharts.chart(
      'dashboard-length-of-time-series', {
        chart: {
          type: 'columnrange',
          inverted: true,
          height: Math.max(120, categories.length * 20 + 80)
        },
        title: { text: null },
        xAxis: {
          categories: categories,
          lineWidth: 0,
          tickLength: 0,
          labels: { enabled: false }
        },
        yAxis: {
          type: 'datetime',
          title: { text: 'Date' }
        },
        legend: { enabled: false },
        plotOptions: {
          columnrange: {
            groupPadding: 0,
            pointPadding: 0
          }
        },
        tooltip: {
          pointFormatter: function () {
            return (
              Highcharts.dateFormat('%Y-%m-%d', this.low) +
              ' - ' +
              Highcharts.dateFormat('%Y-%m-%d', this.high)
            );
          }
        },
        series: [{
          name: 'Length of time series',
          dataLabels: [
            {
              enabled: false
            },
            {
              enabled: true,
              format: '{point.category}',
              align: 'left',
              verticalAlign: 'middle',
              y: -2,
              x: 0,
              crop: false,
              overflow: 'allow'
            }
          ],
          data: data
        }]
      });
  }

  function getNumberOfStationsRange() {
    switch (Number(selectedDashboardNumberStations)) {
      case 1:
        return { min: 0, max: 100 };
      case 2:
        return { min: 100, max: 1000 };
      case 3:
        return { min: 1000, max: 10000 };
      case 4:
        return { min: 10000, max: Infinity };
      default:
        return { min: 0, max: Infinity };
    }
  }

  function renderNumberOfStationsChart() {
    let dataType = getActiveDataTypes();
    let showGGMN = dataType.showGGMN;
    let showObservationsRepository = dataType.showObservationsRepository;
    let range = getNumberOfStationsRange();

    let countries = filterCountries(allCountries).slice().sort(
      function (a, b) {
        return a.name.localeCompare(b.name);
      }
    );

    let themeColors = getThemeColors();

    let categories = [];
    let data = [];
    $.each(countries, function (index, country) {
      let stats = countryStats(
        country, showGGMN, showObservationsRepository
      );
      let countWell = stats ? (stats.count_well || 0) : 0;
      if (countWell < range.min || countWell >= range.max) {
        return;
      }
      let isOdd = categories.length % 2 === 0;
      categories.push(country.name);
      data.push({
        y: countWell,
        color: isOdd ? themeColors.primary : themeColors.secondary
      });
    });

    $('#dashboard-number-of-stations-loading').addClass('hidden');

    if (!categories.length) {
      if (numberOfStationsChart) {
        numberOfStationsChart.destroy();
        numberOfStationsChart = null;
      }
      $('#dashboard-number-of-stations-empty').removeClass('hidden');
      return;
    }
    $('#dashboard-number-of-stations-empty').addClass('hidden');

    numberOfStationsChart = Highcharts.chart(
      'dashboard-number-of-stations', {
        chart: {
          type: 'column',
          height: 400
        },
        title: { text: null },
        xAxis: {
          categories: categories
        },
        yAxis: {
          title: { text: 'Number of stations' }
        },
        legend: { enabled: false },
        plotOptions: {
          column: {
            groupPadding: 0,
            pointPadding: 0
          }
        },
        series: [{
          name: 'Number of stations',
          data: data
        }]
      });
  }

  function selectAllCountries() {
    $('#id_countries').val(
      allCountries.map(function (country) {
        return String(country.id);
      })
    ).trigger('change');
  }

  function renderCountryOptions() {
    let $countriesData = $('#countries-data');
    $countriesData.html(`
        <select name="countries" class="form-control" id="id_countries"
            multiple="" data-select2-id="id_countries">
        </select>
        <div class="select-data-action">
          <div class="select-all-countries">Select all</div>
          <div class="clear-all-countries">Clear all</div>
        </div>
    `)
    let $countries = $('#id_countries');
    $.each(allCountries, function (index, country) {
      $countries.append(
        `<option value="${country.id}">${country.name}</option>`
      );
    });

    $countries.select2({
      placeholder: 'Select countries.'
    });

    $countries.on('change', function () {
      selectedCountries = $('#id_countries').val() || [];
      renderStats();
    });

    $('.select-all-countries').on('click', selectAllCountries);
    $('.clear-all-countries').on('click', function () {
      $('#id_countries').val([]).trigger('change');
    });

    // Select all countries by default.
    selectAllCountries();
  }

  function initWellDashboard(organisationStatisticUrl, countryStatisticUrl) {
    // Init toggle data type
    $('#dashboard-data-type .dashboard-toggle').on('click', function () {
      $(this).toggleClass('active');
      renderStats();
    });

    // Init toggle number of stations
    $('.dashboard-number-stations button').on('click', function () {
      const id = $(this).attr('id');
      selectedDashboardNumberStations = id.replace('dashboard-number-stations-', '');
      $('.dashboard-number-stations button').removeClass('active');
      $(this).addClass('active');
      renderNumberOfStationsChart();
    });

    $.when(
      $.ajax({ url: organisationStatisticUrl, dataType: 'json' }),
      $.ajax({ url: countryStatisticUrl, dataType: 'json' })
    ).done(function (organisationResponse, countryResponse) {
      allOrganisations = (organisationResponse[0] || {}).organisations
        || [];
      allCountries = (countryResponse[0] || {}).countries || [];
      renderCountryOptions();

      $('#dashboard-loading').addClass('hidden');
      $('#dashboard-table').removeClass('hidden');
    }).fail(function () {
      $('#dashboard-loading').addClass('hidden');
      $('#dashboard-error').removeClass('hidden');
    });
  }

  window.initWellDashboard = initWellDashboard;
})(jQuery);