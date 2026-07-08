(function ($) {
    var allOrganisations = [];
    var allCountries = [];

    var ANIMATION_DURATION = 500;
    var RECENTLY_UPDATED_YEARS = 2;

    function formatNumber(value) {
        return Number(value || 0).toLocaleString('en-US');
    }

    function parseNumber(text) {
        return Number(String(text || '0').replace(/,/g, '')) || 0;
    }

    function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    function animateStat($cell, from, to) {
        var startTime = null;

        if (from === to) {
            $cell.text(formatNumber(to));
            return;
        }

        function step(timestamp) {
            if (startTime === null) {
                startTime = timestamp;
            }
            var progress = Math.min(
                (timestamp - startTime) / ANIMATION_DURATION, 1
            );
            var eased = easeOutCubic(progress);
            var current = Math.round(from + (to - from) * eased);
            $cell.text(formatNumber(current));
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        }

        window.requestAnimationFrame(step);
    }

    function setStat(name, value) {
        var $cell = $('[data-stat="' + name + '"]');
        var from = parseNumber($cell.text());
        var to = Number(value) || 0;
        animateStat($cell, from, to);
    }

    function computeStats(organisations) {
        var totals = {
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
            var stats = organisation.data_stats || {};
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

    // country.statistic is the total (GGMN + Well and Monitoring Data),
    // country.statistic_ggmn is the GGMN-only subset. The Well and
    // Monitoring Data (non-GGMN) figures are derived by subtracting
    // statistic_ggmn from statistic.
    function countryStatsForFilters(country, showGgmn, showWellMonitoring) {
        var total = country.statistic || {};
        var ggmn = country.statistic_ggmn || {};

        if (showGgmn && showWellMonitoring) {
            return total;
        }
        if (showGgmn) {
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
        var threshold = new Date();
        threshold.setFullYear(
            threshold.getFullYear() - RECENTLY_UPDATED_YEARS
        );
        return new Date(dateEnd) >= threshold;
    }

    function computeCountryStats(countries, showGgmn, showWellMonitoring) {
        var totals = {
            count_country: 0,
            count_country_recently_updated: 0
        };
        $.each(countries, function (index, country) {
            var stats = countryStatsForFilters(
                country, showGgmn, showWellMonitoring
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

    function getActiveFilters() {
        var filters = [];
        $('.dashboard-filter-toggle.active').each(function () {
            filters.push($(this).data('filter'));
        });
        return filters;
    }

    function filterOrganisations(organisations, filters) {
        var showGgmn = filters.indexOf('ggmn') !== -1;
        var showWellMonitoring = filters.indexOf('well_monitoring') !== -1;
        return $.grep(organisations, function (organisation) {
            if (organisation.is_ggmn) {
                return showGgmn;
            }
            return showWellMonitoring;
        });
    }

    function renderStats() {
        var filters = getActiveFilters();
        var showGgmn = filters.indexOf('ggmn') !== -1;
        var showWellMonitoring = filters.indexOf('well_monitoring') !== -1;

        var filtered = filterOrganisations(allOrganisations, filters);
        var totals = computeStats(filtered);
        $.extend(
            totals,
            computeCountryStats(allCountries, showGgmn, showWellMonitoring)
        );
        $.each(totals, function (key, value) {
            setStat(key, value);
        });
    }

    function initFilters() {
        $('.dashboard-filter-toggle').on('click', function () {
            $(this).toggleClass('active');
            renderStats();
        });
    }

    function initWellDashboard(organisationStatisticUrl, countryStatisticUrl) {
        initFilters();

        $.when(
            $.ajax({url: organisationStatisticUrl, dataType: 'json'}),
            $.ajax({url: countryStatisticUrl, dataType: 'json'})
        ).done(function (organisationResponse, countryResponse) {
            allOrganisations = (organisationResponse[0] || {}).organisations
                || [];
            allCountries = (countryResponse[0] || {}).countries || [];
            renderStats();

            $('#dashboard-loading').addClass('hidden');
            $('#dashboard-table').removeClass('hidden');
        }).fail(function () {
            $('#dashboard-loading').addClass('hidden');
            $('#dashboard-error').removeClass('hidden');
        });
    }

    window.initWellDashboard = initWellDashboard;
})(jQuery);