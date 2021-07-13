const chartColors = [
    "rgb(75, 192, 192)",
    "rgb(255, 99, 132)",
    "rgb(54, 162, 235)",
    "rgb(153, 102, 255)",
    "rgb(255, 205, 86)",
    "rgb(255, 159, 64)",
    "rgb(201, 203, 207)"
]

/** Return year and week of year from date
 */
function getWeekNumber(d) {
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
    var yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    var weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    return [d.getUTCFullYear(), weekNo];
}

/** Format Date into Year-Month-Day **/
function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2)
        month = '0' + month;
    if (day.length < 2)
        day = '0' + day;

    return [year, month, day].join('-');
}

const FROM_TOP_WELL = 'Water depth [from the top of the well]'
const FROM_GROUND_LEVEL = 'Water depth [from the ground surface]'
const FROM_AMSL = 'Water level elevation a.m.s.l.'

function checkLevelParameter(
    parameter_from, parameter_to, value,
    top_borehole_elevation, ground_surface_elevation) {

    switch (parameter_to) {
        case FROM_AMSL:
            switch (parameter_from) {
                case FROM_TOP_WELL:
                    if (!top_borehole_elevation) {
                        return [parameter_from, null]
                    }
                    value = top_borehole_elevation - value;
                    break;
                case FROM_GROUND_LEVEL:
                    if (!ground_surface_elevation) {
                        return [parameter_from, null]
                    }
                    value = ground_surface_elevation - value;
                    break;
                default:
                    break;
            }
            parameter_from = parameter_to;
            break;

        case FROM_GROUND_LEVEL:
            switch (parameter_from) {
                case FROM_TOP_WELL:
                    if (!ground_surface_elevation || !top_borehole_elevation) {
                        return [parameter_from, null]
                    }
                    value = (top_borehole_elevation - ground_surface_elevation) - value;
                    break;
                case FROM_AMSL:
                    if (!ground_surface_elevation) {
                        return [parameter_from, null]
                    }
                    value = value - ground_surface_elevation;
                    break;
                default:
                    value = 0 - value;
                    break;
            }
            parameter_from = parameter_to;
            break;

        case FROM_TOP_WELL:
            switch (parameter_from) {
                case FROM_GROUND_LEVEL:
                    if (!ground_surface_elevation || !top_borehole_elevation) {
                        return [parameter_from, null]
                    }
                    value = 0 - value - (top_borehole_elevation - ground_surface_elevation);
                    break;
                case FROM_AMSL:
                    if (!top_borehole_elevation) {
                        return [parameter_from, null]
                    }
                    value = value - top_borehole_elevation;
                    break;
                default:
                    value = 0 - value;
                    break;
            }
            parameter_from = parameter_to;
            break;
    }
    return [parameter_from, value]
}

function convertMeasurementData(
    input, unit_to, parameter_to,
    top_borehole_elevation, ground_surface_elevation) {
    let data = {};
    input.map(function (row) {
        let parameter = row.par;
        let unit = row.u;
        let value = row.v;
        value = unitConvert(unit, unit_to, value);

        const levelParameter = checkLevelParameter(
            parameter, parameter_to, value,
            top_borehole_elevation, ground_surface_elevation);
        parameter = levelParameter[0];
        value = levelParameter[1];

        // let's we save it
        if (value != null) {
            if (!data[parameter]) {
                data[parameter] = []
            }
            data[parameter].unshift(
                [row.dt * 1000, value]
            );
        }
    })
    return data
}

function renderMeasurementChart(identifier, chart, data, xLabel, yLabel, parameterTo) {
    let title = '';
    switch (identifier) {
        case 'WellLevelMeasurement':
        case 'level_measurement':
            title = 'Groundwater Level';
            break;
        case 'WellQualityMeasurement':
        case 'quality_measurement':
            title = 'Groundwater Quality';
            break;
        case 'WellYieldMeasurement':
        case 'yield_measurement':
            title = 'Abstraction / Discharge';
            break
    }
    if (!data) {
        data = []
    }
    const options = {
        chart: {
            zoomType: 'x'
        },
        title: {
            text: title
        },
        yAxis: {
            title: {
                text: yLabel
            }
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: xLabel
            }
        },
        legend: {
            enabled: false
        },
        rangeSelector: {
            buttons: [{
                type: 'day',
                count: 3,
                text: '3d'
            }, {
                type: 'week',
                count: 1,
                text: '1w'
            }, {
                type: 'month',
                count: 1,
                text: '1m'
            }, {
                type: 'month',
                count: 6,
                text: '6m'
            }, {
                type: 'year',
                count: 1,
                text: '1y'
            }, {
                type: 'all',
                text: 'All'
            }]
        },
        plotOptions: {
            area: {
                fillColor: {
                    linearGradient: {
                        x1: 0,
                        y1: 0,
                        x2: 0,
                        y2: 1
                    },
                    stops: [
                        [0, Highcharts.getOptions().colors[0]],
                        [1, Highcharts.color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                    ]
                },
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            }
        },

        series: [{
            type: 'area',
            name: 'value',
            data: data
        }]
    }
    if (!chart) {
        chart = Highcharts.stockChart(`${identifier}-chart`, options);
    } else {
        chart.update(options);
    }
    return chart;
}

let MeasurementChartObj = function (
    identifier, top_borehole, ground_surface, url, parameters, units,
    $loading, $loadMore, $units, $parameters) {
    this.identifier = identifier;
    this.top_borehole = top_borehole;
    this.ground_surface = ground_surface;
    this.url = url;
    this.$loading = $loading;
    this.$loadMore = $loadMore;
    this.$dataFrom = $loadMore.closest('.measurement-chart-plugin').find('#data-from');
    this.$dataTo = $loadMore.closest('.measurement-chart-plugin').find('#data-to');
    this.$units = $units;
    this.$parameters = $parameters;
    this.data = null;
    this.chart = null;
    this.unitTo = null;
    this.parameterTo = null;
    this.init = true;

    const that = this;
    console.log('test')

    this.asyncRenderChart = function () {
        return new Promise(resolve => {
            that.$loading.show();
            setTimeout(() => {
                that._renderChart();
            }, 100);
        });
    }

    /** Render the chart */
    this._renderChart = function () {
        const data = that.data;
        if (!data) {
            return;
        }
        if (this.init) {
            this.init = false;
            const $paramOptions = $parameters.find(`option:contains(${data?.data[0]?.par})`);
            if ($paramOptions.length > 0) {
                // change the params if the value is not it
                const shouldBe = $($paramOptions[0]).attr('value');
                const currentParam = $parameters.val()
                if (shouldBe !== currentParam) {
                    $parameters.val(shouldBe);
                    $parameters.trigger('change')
                    return false;
                }
            }
        }
        if (data.end) {
            this.$loadMore.attr('disabled', 'disabled')
        } else {
            this.$loadMore.removeAttr('disabled')
        }
        this.$dataTo.html(
            data.data[0] ?
                formatDate(new Date(data.data[0].dt * 1000))
                : 'no data'
        )
        this.$dataFrom.html(
            data.data[data.data.length - 1] ?
                formatDate(new Date(data.data[data.data.length - 1].dt * 1000))
                : 'no data'
        )
        const cleanData = convertMeasurementData(
            data.data, this.unitTo, this.parameterTo,
            unitConvert(
                this.top_borehole.u, this.unitTo, this.top_borehole.v
            ),
            unitConvert(
                this.ground_surface.u, this.unitTo, this.ground_surface.v
            )
        );
        const chartData = cleanData[this.parameterTo];
        this.chart = null;
        if (!chartData || chartData.length === 0) {
            that.$loading.hide();
            $(`#${identifier}-chart`).html('<div style="text-align: center; color: red">No data found</div>')
            return
        }
        this.chart = renderMeasurementChart(
            this.identifier, this.chart,
            cleanData[this.parameterTo],
            'Time', this.parameterTo)
        this.$loading.hide();
    };

    this.renderChart = async function () {
        await that.asyncRenderChart();
    }

    this.refetchData = function () {
        this.fetchData(this.unitTo, this.parameterTo)
    };

    /** Fetch the data */
    this.fetchData = function (unitTo, parameterTo) {
        this.$loading.show();
        this.$loadMore.attr('disabled', 'disabled')
        if (this.url) {
            const that = this;
            $.ajax({
                url: url,
                dataType: 'json',
                data: {
                    page: this.data ? this.data.page : 1,
                },
                success: function (data, textStatus, request) {
                    if (!that.data) {
                        that.data = {
                            data: [],
                            page: 1
                        }
                    }
                    that.data.page += 1;
                    that.data.data = that.data.data.concat(data.data);
                    that.data.end = data.end;
                    if (unitTo === that.unitTo && parameterTo === that.parameterTo) {
                        that.renderChart();
                    }
                },
                error: function (error, textStatus, request) {
                    that.$loading.hide();
                    $(`#${identifier}-chart`).html('<div style="text-align: center; color: red">No data found</div>')
                }
            })
        }
    }

    /** Selection Changed **/
    this.selectionChanged = function () {
        let unitTo = $units.find(":selected").text();
        let parameterTo = $parameters.find(":selected").text();
        if (unitTo !== this.unitTo || parameterTo !== this.parameterTo) {
            this.unitTo = unitTo;
            this.parameterTo = parameterTo;
            if (!that.data) {
                this.fetchData(unitTo, parameterTo);
            } else {
                this.renderChart();
            }
        }
    }

    $parameters.change(function () {
        const parameter = parameters_chart[$(this).val()];
        const unitVal = parseInt($units.val());
        $units.html('');
        $.each(parameter.units, function (index, id) {
            if (id === unitVal) {
                $units.append(`<option value="${id}" selected>${units[id].name}</option>`)
            } else {
                $units.append(`<option value="${id}">${units[id].name}</option>`)
            }
        });
        that.selectionChanged();
    })
    $units.change(function () {
        that.selectionChanged();
    })
    $loadMore.click(function () {
        let unitTo = that.$units.find(":selected").text();
        let parameterTo = that.$parameters.find(":selected").text();
        that.fetchData(unitTo, parameterTo);
        return false;
    })
    $parameters.trigger('change');
}