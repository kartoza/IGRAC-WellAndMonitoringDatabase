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

function checkLevelParameter(
    parameter_from, parameter_to, value,
    top_borehole_elevation, ground_surface_elevation) {
    switch (parameter_to) {
        case 'Water level elevation a.m.s.l.':
            switch (parameter_from) {
                case 'Water depth [from the top of the well]':
                    value = top_borehole_elevation - value;
                    break;
                case 'Water depth [from the ground surface]':
                    value = ground_surface_elevation - value;
                    break;
                default:
                    value = 0 - value;
                    break;
            }
            parameter_from = parameter_to;
            break;

        case 'Water depth [from the ground surface]':
            switch (parameter_from) {
                case 'Water depth [from the top of the well]':
                    value = (top_borehole_elevation - ground_surface_elevation) - value;
                    break;
                case 'Water level elevation a.m.s.l.':
                    value = value - ground_surface_elevation;
                    break;
                default:
                    value = 0 - value;
                    break;
            }
            parameter_from = parameter_to;
            break;

        case 'Water depth [from the top of the well]':
            switch (parameter_from) {
                case 'Water depth [from the ground surface]':
                    value = 0 - value - (top_borehole_elevation - ground_surface_elevation);
                    break;
                case 'Water level elevation a.m.s.l.':
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
    input, unit_to, parameter_to, time_range,
    top_borehole_elevation, ground_surface_elevation) {
    let data = {};
    let timeRangeData = {};
    input.map(function (row) {
        let parameter = row.par;
        let unit = row.u;

        let skip = false;
        switch (time_range) {
            case 'hourly': {
                // this is for hourly
                let value = row.v;
                value = unitConvert(unit, unit_to, value);

                // skip if no value
                if (value === undefined || value === null) {
                    skip = true;
                    break
                }
                const levelParameter = checkLevelParameter(
                    parameter, parameter_to, value,
                    top_borehole_elevation, ground_surface_elevation);
                parameter = levelParameter[0];
                value = levelParameter[1];

                // let's we save it
                if (!data[parameter]) {
                    data[parameter] = []
                }
                data[parameter].push({
                    t: new Date(row.dt * 1000),
                    y: value,
                    methodology: row.mt,
                    unit: unit_to
                });
                break
            }
            default:
                console.log(row.v)
                timeRangeData[row.dt] = {
                    'max': checkLevelParameter(
                        parameter, parameter_to, unitConvert(unit, unit_to, row.v.max),
                        top_borehole_elevation, ground_surface_elevation)[1],
                    'min': checkLevelParameter(
                        parameter, parameter_to, unitConvert(unit, unit_to, row.v.min),
                        top_borehole_elevation, ground_surface_elevation)[1],
                    'median': checkLevelParameter(
                        parameter, parameter_to, unitConvert(unit, unit_to, row.v.med),
                        top_borehole_elevation, ground_surface_elevation)[1],
                    'average': checkLevelParameter(
                        parameter, parameter_to, unitConvert(unit, unit_to, row.v.avg),
                        top_borehole_elevation, ground_surface_elevation)[1]
                };
                break
        }

        // skip it if skip
        if (skip) {
            return
        }
    })

    let labels = Object.keys(timeRangeData).reverse();
    if (labels.length > 0) {
        // reconstruct data by timeRangeData
        $.each(labels, function (idx, key) {
            const value = timeRangeData[key];
            // Max of data
            if (!data['max']) {
                data['max'] = []
            }
            data['max'].push({
                x: key,
                y: value['max'],
                unit: unit_to
            })

            // Min of data
            if (!data['min']) {
                data['min'] = []
            }
            data['min'].push({
                x: key,
                y: value['min'],
                unit: unit_to
            })

            if (!data['average']) {
                data['average'] = []
            }
            data['average'].push({
                x: key,
                y: value['median'],
                unit: unit_to
            })

            if (!data['median']) {
                data['median'] = []
            }
            data['median'].push({
                x: key,
                y: value['median'],
                unit: unit_to
            })
        });
    }
    return {
        data: data,
        labels: labels
    }
}

function renderMeasurementChart(identifier, chart, rawData, xLabel, yLabel) {
    let ctx = document.getElementById(`${identifier}-chart`).getContext("2d");
    let dataset = [];
    let idx = 0;
    $.each(rawData.data, function (key, value) {
        dataset.push({
            label: key,
            data: value,
            backgroundColor: chartColors[idx],
            borderColor: chartColors[idx],
            borderWidth: 1,
            fill: false,
            lineTension: 0,
            pointRadius: 1,
            pointHoverRadius: 5,
        })
        idx += 1;
    });
    const options = {
        type: 'line',
        data: {
            datasets: dataset
        },
        options: {
            legend: {
                display: false
            },
            scales: {
                xAxes: [{
                    type: 'time',
                    scaleLabel: {
                        display: true,
                        labelString: xLabel
                    }
                }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: yLabel
                    }
                }]
            },
            tooltips: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function (tooltipItem, allData) {
                        let data = allData.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                        let label = tooltipItem.yLabel + ' ' + data.unit;
                        if (data.methodology) {
                            label += ', methodology :' + data.methodology;
                        }
                        return ' ' + label;
                    }
                }
            }
        }
    };

    // show legend if data is more than 2 dataset
    // and show it as not time
    if (Object.keys(rawData.data).length > 1) {
        options.options.legend.display = true
    }
    // if there is label, xAxes turns to be string
    if (rawData.labels.length > 0) {
        options.options.scales.xAxes = [{
            scaleLabel: {
                display: true,
                labelString: xLabel
            },
            ticks: {
                maxTicksLimit: 20,
                display: true,
            },
        }]
        options.data.labels = rawData.labels;
    }

    if (!chart) {
        chart = new Chart(ctx, options);
    } else {
        chart.data = options.data;
        chart.options = options.options;
        chart.update();
    }
    return chart;
}

let MeasurementChartObj = function (
    identifier, top_borehole, ground_surface, url, parameters, units,
    $loading, $loadMore, $units, $parameters, $timeRange) {
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
    this.$timeRange = $timeRange;

    this.data = {};
    this.chart = null;
    this.unitTo = null;
    this.parameterTo = null;
    this.timeRange = null;

    /** Render the chart */
    this.renderChart = function () {
        const data = that.data[this.timeRange]
        this.$loading.hide();
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
            data.data, this.unitTo, this.parameterTo, this.timeRange,
            unitConvert(
                this.top_borehole.u, this.unitTo, this.top_borehole.v
            ),
            unitConvert(
                this.ground_surface.u, this.unitTo, this.ground_surface.v
            )
        )
        this.chart = renderMeasurementChart(
            this.identifier, this.chart, cleanData, 'Time', this.parameterTo)
    }

    this.refetchData = function () {
        this.fetchData(this.unitTo, this.parameterTo, this.timeRange)
    }

    /** Fetch the data */
    this.fetchData = function (unitTo, parameterTo, timeRange) {
        this.$loading.show();
        this.$loadMore.attr('disabled', 'disabled')
        if (this.url) {
            const that = this;
            $.ajax({
                url: url,
                dataType: 'json',
                data: {
                    page: this.data.page,
                    mode: timeRange
                },
                success: function (data, textStatus, request) {
                    if (!that.data[timeRange]) {
                        that.data[timeRange] = {
                            data: [],
                            page: 1
                        }
                    }
                    that.data[timeRange].page += 1;
                    that.data[timeRange].data = that.data[timeRange].data.concat(data.data);
                    that.data[timeRange].end = data.end;
                    if (unitTo === that.unitTo && parameterTo === that.parameterTo && timeRange === that.timeRange) {
                        that.renderChart();
                        that.$loading.hide();
                    }
                },
                error: function (error, textStatus, request) {
                }
            })
        }
    }

    /** Selection Changed **/
    this.selectionChanged = function () {
        let unitTo = $units.find(":selected").text();
        let parameterTo = $parameters.find(":selected").text();
        let timeRange = $timeRange.val();
        if (!timeRange) {
            timeRange = 'hourly'
        }
        if (unitTo !== this.unitTo || parameterTo !== this.parameterTo || timeRange !== this.timeRange) {
            this.unitTo = unitTo;
            this.parameterTo = parameterTo;
            this.timeRange = timeRange;
            if (!that.data[timeRange]) {
                this.fetchData(unitTo, parameterTo, timeRange);
            } else {
                this.renderChart();
            }
        }
    }

    const that = this;
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
    $timeRange.change(function () {
        that.selectionChanged();
    })
    $loadMore.click(function () {
        let unitTo = that.$units.find(":selected").text();
        let parameterTo = that.$parameters.find(":selected").text();
        let timeRange = that.$timeRange.val();
        that.fetchData(unitTo, parameterTo, timeRange);
        return false;
    })
    $parameters.trigger('change');
}