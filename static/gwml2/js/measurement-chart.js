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
/** Get param group **/
function getParamGroup (paramInput) {
    let group = ''
    $.each(parameters_chart, function (header_name, parameters) {
        $.each(parameters, function (idx, param) {
            if (param.name === paramInput) {
                group = header_name;
                return false;
            }
        })
        if (group) {
            return false;
        }
    });
    return group
}

const FROM_TOP_WELL = 'Water depth [from the top of the well]'
const FROM_GROUND_LEVEL = 'Water depth [from the ground surface]'
const FROM_AMSL = 'Water level elevation a.m.s.l.'
const measurementAverage = arr => arr.reduce((p, c) => p + c[1], 0) / arr.length;

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

        // ------------------------------------------------
        // Just groundwater level params
        let level_parameters = [FROM_AMSL, FROM_GROUND_LEVEL, FROM_TOP_WELL]
        if (level_parameters.includes(parameter)){
            const levelParameter = checkLevelParameter(
                parameter, parameter_to, value,
                top_borehole_elevation, ground_surface_elevation);
            parameter = levelParameter[0];
            value = levelParameter[1];
        }
        // ------------------------------------------------

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

/**
 * Get the trendlines data
 */
function getTrendlines(chartData, steps) {
    try {
        const defaultFirstStep = chartData[0][0] - 10;
        const defaultLastStep = chartData[chartData.length - 1][0] + 10;

        // we need to construct steps
        if (steps.length === 0) {
            steps = [defaultFirstStep, defaultLastStep]
        } else {
            steps = [defaultFirstStep].concat(steps).concat([defaultLastStep]);
        }
        steps = steps.sort(function (a, b) {
            return a - b;
        });

        let data = []
        let prevStep = null;
        let jumps = [];
        steps.forEach(function (step) {
            if (prevStep) {
                const filteredData = chartData.filter(function (row) {
                        return prevStep <= row[0] && row[0] < step
                    }
                );
                const average = measurementAverage(filteredData);
                const cleanData = filteredData.map(item => {
                    return [item[0], average]
                })
                if (cleanData[0] && cleanData[cleanData.length - 1]) {
                    jumps.push([cleanData[0], cleanData[cleanData.length - 1]]);
                }
                data = data.concat(cleanData);
            }
            prevStep = step
        });
        return [data, jumps]
    } catch (e) {
        console.log(e)
        return [[], []]
    }
}

function renderMeasurementChart(identifier, chart, data, xLabel, yLabel, stepTrenlineData, toggleSeries, onChartClicked, title = '') {
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
            zoomType: 'x',
            events: {
                click: function (event) {
                    onChartClicked(new Date(event.xAxis[0].value))
                }
            }
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
            enabled: true
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
            series: {
                showInLegend: false,
                dataGrouping: { groupPixelWidth: 50, units: [['hour', [4]], ['day', [1]], ['week', [1, 2]], ['month', [1]]] }
            }
        },
        series: [
            {
                id: 'value',
                name: title,
                data: data,
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
                lineWidth: 2,
                states: {
                    hover: {
                        lineWidth: 2
                    }
                },
                threshold: null,
                color: '#24619d',
                tooltip: {
                    valueDecimals: 3
                },
                events: {
                    hide: function (e) {
                        toggleSeries['value'] = false;
                    },
                    show: function (e) {
                        toggleSeries['value'] = true;
                    }
                },
                visible: toggleSeries['value']
            },
            {
                name: 'Trend Line',
                linkedTo: 'value',
                type: 'trendline',
                tooltip: {
                    valueDecimals: 0
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                color: '#F48020',
                events: {
                    hide: function (e) {
                        toggleSeries['trend'] = false;
                    },
                    show: function (e) {
                        toggleSeries['trend'] = true;
                    }
                },
                visible: toggleSeries['trend']
            },
            {
                type: 'spline',
                name: 'Step Trendline',
                data: stepTrenlineData,
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                color: '#F48020',
                tooltip: {
                    valueDecimals: 3
                },
                visible: toggleSeries['step'],
                events: {
                    hide: function (e) {
                        toggleSeries['step'] = false;
                    },
                    show: function (e) {
                        toggleSeries['step'] = true;
                    }
                }
            }
        ]
    }
    if (!chart) {
        chart = Highcharts.stockChart(`${identifier}-chart`, options);
    } else {
        chart.update(options);
    }
    return chart;
}

let MeasurementChartObj = function (
    identifier, top_borehole, ground_surface, urls, parameters, units,
    $loading, $loadMore, $units, $parameters) {
    this.identifier = identifier;
    this.top_borehole = top_borehole;
    this.ground_surface = ground_surface;
    this.urls = urls;
    this.$loading = $loading;
    this.$loadMore = $loadMore;
    this.$dataFrom = $loadMore.closest('.measurement-chart-plugin').find('#data-from');
    this.$dataTo = $loadMore.closest('.measurement-chart-plugin').find('#data-to');
    this.$units = $units;
    this.$parameters = $parameters;
    this.$trend = $(`#${identifier}-trend`);
    this.data = null;
    this.chart = null;
    this.unitTo = null;
    this.parameterTo = null;
    this.init = true;
    this.steps = [];
    this.stepsString = [];
    this.$stepTimeSelection = $(`#${identifier}-step-time`);
    this.$stepList = $(`#${identifier}-step-list`);
    this.$stepDescription = $(`#${identifier}-step-description`);
    this.toggleSeries = {
        value: true,
        trend: true,
        step: false
    };
    this.isTrendLine = false;

    const that = this;
    // The step event initiation
    this.$stepTimeSelection.attr('autocomplete', 'off');
    const onNewStep = function (stepInput) {
        const d = new Date(stepInput)
        d.setSeconds(0);

        const year = d.getFullYear();
        const month = ("0" + (d.getMonth() + 1)).slice(-2);
        const day = ("0" + d.getDate()).slice(-2);
        const hour = ("0" + d.getHours()).slice(-2);
        const minute = ("0" + d.getMinutes()).slice(-2);
        const second = ("0" + d.getSeconds()).slice(-2);
        const newStepString = `${year}-${month}-${day} ${hour}:${minute}:${second}`;

        const newStep = d.getTime();
        if (!that.stepsString.includes(newStepString)) {
            that.stepsString.push(newStepString);
            that.steps.push(newStep);

            const stepsString = that.stepsString.sort();
            const steps = that.steps.sort(function (a, b) {
                return a - b;
            });
            that.$stepList.html('');
            steps.forEach(function (item, idx) {
                newStepElement(steps[idx], stepsString[idx]);
                that.renderChart();
            })
        }
    }
    const newStepElement = function (newStep, newStepString) {
        const stepId = `${identifier}-${newStep}`
        that.$stepList.append(
            `<div id="${stepId}" class="step-data">
                <input value="${newStepString}" type="text" name="time"> 
                <i class="fa fa-minus-circle" aria-hidden="true" data-step="${newStep}" data-step-string="${newStepString}"></i></div>`);
        const $step = $(`#${stepId}`);

        $step.find('i').click(function () {
            const deletedStep = $(this).data('step');
            const deletedStepString = $(this).data('step-string');
            that.steps = that.steps.filter(function (e) {
                return e !== deletedStep
            })
            that.stepsString = that.stepsString.filter(function (e) {
                return e !== deletedStepString
            })
            $step.remove();
            that.renderChart();
        })
        $step.find('input').datetimepicker({
            formatTime: 'H:i',
            format: 'Y-m-d H:i',
            onClose: function (dp, $input) {
                $step.find('i').click();
                const newStep = new Date(dp).getTime();
                const val = $input.val();
                if (val) {
                    onNewStep(newStep);
                }
            }
        })
    }
    this.$stepTimeSelection.datetimepicker({
        formatTime: 'H:i',
        format: 'Y-m-d H:i',
        onClose: function (dp, $input) {
            const newStep = new Date(dp).getTime();
            const val = $input.val();
            if (val) {
                onNewStep(newStep);
            }
        }
    })

    this.asyncRenderChart = function () {
        return new Promise(resolve => {
            that.$loading.show();
            setTimeout(() => {
                that._renderChart();
            }, 100);
        });
    }

    /** Update selection **/
    const updateSelection = (data) => {
        if (!data) {
            data = {data: []}
        }

        // check the param options
        const parameters = Array.from(new Set(data.data.map(row => row.par)));
        if (parameters.includes(FROM_TOP_WELL) || parameters.includes(FROM_GROUND_LEVEL) || parameters.includes(FROM_AMSL)) {
            if (that.top_borehole?.v) {
                parameters.push(FROM_TOP_WELL)
                parameters.push(FROM_AMSL)
            }
            if (that.ground_surface?.u) {
                parameters.push(FROM_GROUND_LEVEL)
                parameters.push(FROM_AMSL)
            }
        }
        // Hide non found one
        $parameters.find('option').each(function(index) {
            if (parameters.includes($(this).text())) {
                $(this).show()
            } else {
                $(this).attr('hidden', true)
            }
        });
        const parameterGroups = []
        parameters.map(param => {
            parameterGroups.push(getParamGroup(param))
        })
        $parameters.find('optgroup').each(function(index) {
            if (parameterGroups.includes($(this).attr('label'))) {
                $(this).show()
            } else {
                $(this).attr('hidden', true)
            }
        });
    }

    /** Render the chart */
    this._renderChart = function () {
        const data = that.data;
        updateSelection(data)
        if (!data) {
            return;
        }

        // Autoselect the first options
        if (this.init) {
            this.init = false;
            const $params = $($parameters.find('option:not(option[hidden])')[0])
            if ($params?.length) {
                // change the params if the value is not it
                const shouldBe = $params.attr('value');
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
            $(`#${identifier}-chart`).html('<div class="Error">No data found</div>');
            $(`#${identifier}-step`).hide();
            return
        }

        // calculate the step trendlines
        const trenlineDataOutput = getTrendlines(chartData, this.steps);
        const trenlineData = trenlineDataOutput[0];
        const trenlineJumps = trenlineDataOutput[1];

        // create jumps notification
        const differences = [];
        trenlineJumps.forEach(function (jump, idx) {
            try {
                differences.push((trenlineJumps[idx][0][1] - trenlineJumps[idx - 1][1][1]).toFixed(2));
            } catch (e) {
            }
        })
        that.$stepDescription.html('');
        that.$stepDescription.hide();
        if (differences.length === 1) {
            that.$stepDescription.html('There is difference : ' + differences.join(', '));
            that.$stepDescription.show();
        } else if (differences.length > 1) {
            that.$stepDescription.html('There are differences : ' + differences.join(', '));
            that.$stepDescription.show();
        }

        let title = getParamGroup(this.parameterTo)
        this.chart = renderMeasurementChart(
            this.identifier, this.chart,
            cleanData[this.parameterTo],
            'Time', this.parameterTo, trenlineData, this.toggleSeries,
            function (date) {
                // when chart is clicked
                if (that.isTrendLine) {
                    onNewStep(date.getTime());
                }
            },
            title
        )
        this.$loading.hide();
    };

    this.renderChart = async function () {
        await that.asyncRenderChart();
    };

    this.refetchData = function () {
        this.fetchData(this.unitTo, this.parameterTo)
    };

    /** Fetch the data */
    this.fetchData = function (unitTo, parameterTo) {
        this.$loading.show();
        this.$loadMore.attr('disabled', 'disabled')
        if (this.urls) {
            const that = this;
            $.each(this.urls, function (idx, url) {
                if (!url) {
                    return
                }
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
                        updateSelection( that.data)
                    }
                })
            });
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
        let parameter = null;
        const paramValue = $(this).val()
        $.each(parameters_chart, function (header_name, parameters) {
            if(parameters[paramValue]){
                parameter = parameters[paramValue]
            }
        });
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

    this.$trend.change(function () {
        const chart = that.chart;
        $(`#${identifier}-step`).hide();
        that.isTrendLine = false;
        if (chart) {
            chart.series[0].show();
            switch ($(this).val()) {
                case 'both':
                    chart.series[1].show();
                    chart.series[2].show();
                    $(`#${identifier}-step`).show();
                    that.isTrendLine = true;
                    break
                case 'linear':
                    chart.series[1].show();
                    chart.series[2].hide();
                    break
                case 'step':
                    chart.series[1].hide();
                    chart.series[2].show();
                    $(`#${identifier}-step`).show();
                    that.isTrendLine = true;
                    break
                case 'no':
                    chart.series[1].hide();
                    chart.series[2].hide();
                    break
            }
        }
    })
}