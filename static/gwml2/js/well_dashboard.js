(function ($) {
    var allOrganisations = [];

    var ANIMATION_DURATION = 500;

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
        var filtered = filterOrganisations(
            allOrganisations, getActiveFilters()
        );
        var totals = computeStats(filtered);
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

    function initWellDashboard(statisticUrl) {
        initFilters();

        $.ajax({
            url: statisticUrl,
            dataType: 'json'
        }).done(function (data) {
            allOrganisations = data.organisations || [];
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