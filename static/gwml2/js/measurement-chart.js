const chartColors = [
    "rgb(255, 99, 132)",
    "rgb(54, 162, 235)",
    "rgb(153, 102, 255)",
    "rgb(255, 205, 86)",
    "rgb(75, 192, 192)",
    "rgb(255, 159, 64)",
    "rgb(201, 203, 207)"
]

function convertMeasurementData(input, unit_to, parameter_to, top_borehole_elevation, ground_surface_elevation) {
    let data = {};
    input.map(function (row) {
        let parameter = row['par'];
        let value = row['v'];
        let methodology = row['mt'];
        let unit = row['u'];
        let time = row['dt'];
        value = unitConvert(unit, unit_to, value);

        switch (parameter_to) {
            case 'Water level elevation a.m.s.l.':
                switch (parameter) {
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
                parameter = parameter_to;
                break;

            case 'Water depth [from the ground surface]':
                switch (parameter) {
                    case 'Water depth [from the top of the well]':
                        value = (top_borehole_elevation - ground_surface_elevation) - value;
                        break;
                    case 'Water level elevation a.m.s.l':
                        value = ground_surface_elevation - value;
                        break;
                    default:
                        value = 0 - value;
                        break;
                }
                parameter = parameter_to;
                break;

            case 'Water depth [from the top of the well]':
                switch (parameter) {
                    case 'Water depth [from the ground surface]':
                        value = 0 - value - (top_borehole_elevation - ground_surface_elevation);
                        break;
                    case 'Water level elevation a.m.s.l':
                        value = top_borehole_elevation - value;
                        break;
                    default:
                        value = 0 - value;
                        break;
                }
                parameter = parameter_to;
                break;
        }


        if (!data[parameter]) {
            data[parameter] = []
        }
        if (parameter === parameter_to) {
            data[parameter].push({
                t: new Date(time * 1000),
                y: value,
                methodology: methodology,
                unit: unit_to
            });
        }
    })
    return data;
}

function renderMeasurementChart(identifier, chart, data, xLabel, yLabel) {
    let ctx = document.getElementById(`${identifier}-chart`).getContext("2d");
    let dataset = [];
    let idx = 0;
    $.each(data, function (key, value) {
        dataset.push({
            label: key,
            data: value,
            backgroundColor: chartColors[idx],
            borderColor: chartColors[idx],
            borderWidth: 1,
            fill: false,
            lineTension: 0
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
                mode: 'point',
                intersect: true,
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
    this.$units = $units;
    this.$parameters = $parameters;
    this.$timeRange = $timeRange;

    this.data = {
        data: [],
        page: 1
    };
    this.chart = null;
    this.unitTo = null;
    this.parameterTo = null;
    this.timeRange = null;

    /** Render the chart */
    this.renderChart = function () {
        if (this.data.end) {
            this.$loadMore.attr('disabled', 'disabled')
        } else {
            this.$loadMore.removeAttr('disabled')
        }
        const cleanData = convertMeasurementData(
            this.data.data, this.unitTo, this.parameterTo,
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

    /** Fetch the data */
    this.fetchData = function (unitTo, parameterTo, timeRange) {
        this.$loading.show();
        this.$loadMore.attr('disabled', 'disabled')
        const that = this;
        $.ajax({
            url: url,
            dataType: 'json',
            data: {
                page: this.data.page,
                timerange: timeRange
            },
            success: function (data, textStatus, request) {
                that.data.page += 1;
                that.data.data = that.data.data.concat(data.data);
                that.data.end = data.end;
                if (unitTo === that.unitTo && parameterTo === that.parameterTo && timeRange === that.timeRange) {
                    that.renderChart();
                    that.$loading.hide();
                }
            },
            error: function (error, textStatus, request) {
            }
        })
    }

    /** Selection Changed **/
    this.selectionChanged = function () {
        let unitTo = $units.find(":selected").text();
        let parameterTo = $parameters.find(":selected").text();
        let timeRange = $timeRange.val();
        if (unitTo !== this.unitTo || parameterTo !== this.parameterTo || timeRange !== this.timeRange) {
            this.unitTo = unitTo;
            this.parameterTo = parameterTo;
            this.timeRange = timeRange;
            if (this.data.data.length === 0) {
                this.fetchData(unitTo, parameterTo, timeRange);
            } else {
                this.renderChart();
            }
        }
    }

    const that = this;
    $parameters.change(function () {
        const parameter = parameters[$(this).val()];
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
    })
    $parameters.trigger('change');
}