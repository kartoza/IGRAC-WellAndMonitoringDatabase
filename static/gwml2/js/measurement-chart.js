function renderMeasurementChart($chart, id, data, xLabel, yLabel, parameters, parameter_to, units, unit_to) {
    $chart.html(`<canvas id="${id}_chart_canvas"></canvas>`);

    // render parameters and unit selection
    {
        let html = '<select class="parameter-selection">';
        parameters.forEach(function (param) {
            if (parameter_to === param) {
                html += `<option value="${param}" selected>` + param + '</option>'
            } else {
                html += `<option value="${param}">` + param + '</option>'
            }
        })
        html += '</select>';
        html += '<select class="unit-selection">';
        units.forEach(function (unit) {
            if (unit_to === unit) {
                html += `<option value="${unit}" selected>` + unit + '</option>'
            } else {
                html += `<option value="${unit}">` + unit + '</option>'
            }
        })
        html += '</select><br><br><br>';
        $chart.prepend(html);
        $chart.find('select').change(function () {
            chartFunctions[id](
                $chart.find('.parameter-selection').val(),
                $chart.find('.unit-selection').val()
            )
        })
    }
    var ctx = document.getElementById(`${id}_chart_canvas`).getContext("2d");
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
    new Chart(ctx, {
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
                        let label = allData.datasets[tooltipItem.datasetIndex].label || '';
                        let data = allData.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                        if (label) {
                            label += ' : ';
                        }
                        label += tooltipItem.yLabel;
                        if (data.methodology) {
                            label += ', methodology :' + data.methodology;
                        }
                        return ' ' + label;
                    }
                }
            }
        },
    });
}