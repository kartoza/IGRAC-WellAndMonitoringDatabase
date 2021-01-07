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

let chart = null;

function renderMeasurementChart(identifier, data, xLabel, yLabel) {
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
}