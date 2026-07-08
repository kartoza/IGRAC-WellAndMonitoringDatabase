(function ($) {
  let allOrganisations = [];
  let allCountries = [];
  let selectedCountries = [];

  let ANIMATION_DURATION = 500;
  let RECENTLY_UPDATED_YEARS = 2;

  function computeStats(organisations) {
    let totals = {
      count_organisation: organisations.length,
      count_well: 0,
      count_well_with_level: 0,
      count_well_with_quality: 0,
      count_spring: 0,
      count_measurement_level: 0,
      count_measurement_quality: 0,
      count_automatic_connection: 0
    };
    $.each(organisations, function (index, organisation) {
      let stats = organisation.data_stats || {};
      totals.count_well += stats.count_well || 0;
      totals.count_well_with_level +=
        stats.count_well_with_level || 0;
      totals.count_well_with_quality +=
        stats.count_well_with_quality || 0;
      totals.count_spring += stats.count_spring || 0;
      totals.count_measurement_level +=
        stats.count_measurement_level || 0;
      totals.count_measurement_quality +=
        stats.count_measurement_quality || 0;
      if (organisation.data_is_from_api) {
        totals.count_automatic_connection += 1;
      }
    });
    return totals;
  }

  function countryStatsForFilters(country, showGGMN, showWellMonitoring) {
    let total = country.statistic || {};
    let ggmn = country.statistic_ggmn || {};

    if (showGGMN && showWellMonitoring) {
      return total;
    }
    if (showGGMN) {
      return ggmn;
    }
    if (showWellMonitoring) {
      return {
        count_well: (total.count_well || 0) - (ggmn.count_well || 0),
        data_date_end: total.data_date_end
      };
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

  function computeCountryStats(countries, showGGMN, showWellMonitoring) {
    let totals = {
      count_country: 0,
      count_country_recently_updated: 0
    };
    $.each(countries, function (index, country) {
      let stats = countryStatsForFilters(
        country, showGGMN, showWellMonitoring
      );
      if (!stats || (stats.count_well || 0) <= 0) {
        return;
      }
      totals.count_country += 1;
      if (isRecentlyUpdated(stats.data_date_end)) {
        totals.count_country_recently_updated += 1;
      }
    });
    return totals;
  }

  function isCountryOrganisationVisible(organisation) {
    if (!organisation.country_name) {
      return true;
    }
    return selectedCountries.indexOf(organisation.country_name) !== -1;
  }

  function filterOrganisations(organisations, filters) {
    let showGGMN = filters.indexOf('ggmn') !== -1;
    let showWellMonitoring = filters.indexOf('well_monitoring') !== -1;
    return $.grep(organisations, function (organisation) {
      if (!isCountryOrganisationVisible(organisation)) {
        return false;
      }
      if (organisation.is_ggmn) {
        return showGGMN;
      }
      return showWellMonitoring;
    });
  }

  function filterCountries(countries) {
    return $.grep(countries, function (country) {
      return selectedCountries.indexOf(country.name) !== -1;
    });
  }

  function renderStats() {
    let filters = [];
    $('.dashboard-filter-toggle.active').each(function () {
      filters.push($(this).data('filter'));
    });
    let showGGMN = filters.indexOf('ggmn') !== -1;
    let showWellMonitoring = filters.indexOf('well_monitoring') !== -1;

    let filtered = filterOrganisations(allOrganisations, filters);
    let totals = computeStats(filtered);
    $.extend(
      totals,
      computeCountryStats(
        filterCountries(allCountries), showGGMN, showWellMonitoring
      )
    );
    $.each(totals, function (key, value) {
      let $cell = $('[data-stat="' + key + '"]');
      let from = WellDashboardUtils.parseNumber($cell.text());
      let to = Number(value) || 0;
      WellDashboardUtils.animateStat($cell, from, to, ANIMATION_DURATION);
    });
  }

  function selectAllCountries() {
    $('#id_countries').val(
      allCountries.map(function (country) {
        return country.name;
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
        `<option value="${country.name}">${country.name}</option>`
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
    $('.dashboard-filter-toggle').on('click', function () {
      $(this).toggleClass('active');
      renderStats();
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