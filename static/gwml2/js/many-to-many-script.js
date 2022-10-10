function deleteRelation(elm) {
    /*** Deleting relation of many to many
     *
     * @type {boolean}
     */
    if (!$(elm).data('url')) {
        $(elm).closest('tr').remove()
        return;
    }
    var r = confirm("Are you sure want to delete this?");
    if (r === true) {
        $.ajax({
            url: $(elm).data('url'),
            type: "POST",
            cache: false,
            contentType: false,
            processData: false,
            beforeSend: function (xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", $('*[name=csrfmiddlewaretoken]').val());
                }
            },
            success: function (data) {
                $(elm).closest('tr').remove()
            },
            error: function (error) {
                alert(error['responseText'])
            }
        });
    }
}

function parameterChanged($inputParameter, $inputUnit, $inputValue) {
    if ($inputParameter.find('option').length === 1) {
        return
    }
    let parametersSelected = $inputParameter.val()
    let units = parameters[parametersSelected] || [];
    let $option = $inputUnit.find('option');
    let val = $inputUnit.val()
    $option.each(function (index) {
        if (units.includes($(this).attr('value'))) {
            $(this).show();
            $(this).removeAttr('hidden')
        } else {
            $(this).hide();
            $(this).attr('hidden', 'hidden')
            $(this).removeAttr('selected');
            if (val === $(this).attr('value')) {
                $inputUnit.val('')
            }
        }
    });
    // make default value
    if ($inputUnit.find('option:selected').length === 0 && $inputUnit.find("option:not([hidden='hidden'])").length > 0) {
        $inputUnit.val($($inputUnit.find("option:not([hidden='hidden'])")[0]).attr('value'))
    }
    // make default value attributes
    if ($inputValue.data('min') !== undefined) {
        $inputValue.attr('min', $inputValue.data('min'))
    } else {
        $inputValue.removeAttr('min')
    }
    if ($inputValue.data('max') !== undefined) {
        $inputValue.attr('max', $inputValue.data('max'))
    } else {
        $inputValue.removeAttr('max')
    }

    // if the parameter is ph
    if ($inputParameter.find("option:selected").text().toLowerCase().includes('ph')) {
        $inputValue.attr('min', 0)
        $inputValue.attr('max', 14)
    }
}

function initRowData($row) {
    let $inputTime = $row.find('input[name="time"]');
    if ($inputTime.length > 0) {
        $inputTime.attr('autocomplete', 'off');
        $inputTime.datetimepicker({
            formatTime: 'H:i',
            format: 'Y-m-d H:i',
        });
    }

    // parameters
    let $inputParameter = $row.find('select[name="parameter"]');
    if ($inputParameter.length > 0) {
        let $inputUnit = $row.find('select[name="value_unit"]');
        let $inputValue = $row.find('input[name="value_value"]');
        $inputParameter.change(function () {
            parameterChanged($inputParameter, $inputUnit, $inputValue);
        });
        $inputParameter.trigger('change')
    }
    $row.find('input,select,textarea').change(function () {
        $row.addClass('updated')
    });

    // parameters
    let $detailInput = $row.find('input[name="info"]');
    if ($detailInput.length > 0) {
        if ($detailInput.val()) {
            $detailInput.replaceWith(
                `<i class="fa fa-info-circle" data-toggle="tooltip" aria-hidden="true" title="${$detailInput.val().replaceAll('&#013;', '\n')}"></i>`)
            $row.find('.fa-info-circle').tooltip();
        } else {
            $detailInput.replaceWith(``)
        }
    }
}

/** add new row, and put data if presented **/
function addNewRow($table, template, data) {
    let $tbody = $table.find('tbody');
    let $wrapper = $table.closest('.table-wrapper')
    $tbody.prepend(template.content.cloneNode(true));
    let $row = $tbody.find('tr').first();
    initRowData($row)
    $wrapper.scrollTop(0)

    // insert data into row
    if (data) {
        $.each(data, function (key, value) {
            key = key.toLowerCase()
            key = key === 'value' ? 'value_value' : key
            key = key === 'unit' ? 'value_unit' : key
            let $input = $row.find(`*[name=${key}]`);
            if ($input.length > 0) {
                if ($input.is('select')) {
                    $input.find('option').each(function (index) {
                        if ($(this).html() === value || $(this).attr('value') === value) {
                            $input.val($(this).attr('value'))
                        }
                    })
                } else {
                    $input.val(value)
                }
            }
        });
    }
}

function addRowData($table, html) {
    let $tbody = $table.find('tbody');
    $tbody.append(html);
    let $row = $tbody.find('tr').last();
    initRowData($row)
}

function fetchManyToMany($element, set) {
    let $wrapper = $element;
    let $manyToMany = $element.closest('.many-to-many');
    let $table = $element.find('table');
    $wrapper.attr('disabled', true);

    // show loading on chart
    const chart = measurementCharts[$manyToMany.attr('id')];
    if (chart) {
        chart.$loading.show();
        chart.$loadMore.attr('disabled', 'disabled')
    }

    return $.ajax({
        url: $element.data('fetchurl'),
        dataType: 'json',
        data: {
            set: set
        },
        beforeSend: function (xhrObj) {
        },
        success: function (data, textStatus, request) {
            $.each(data['data'], function (index, value) {
                let lastColumn =
                    `<td data-url="${value['delete_url']}" onclick="deleteRelation(this)">
                        <img class="icon-svg delete" src="/static/gwml2/svg/delete.svg"/>
                     </td>`;
                if (readOnly) {
                    lastColumn = '';
                }
                addRowData(
                    $table,
                    '<tr>' + value['html'].replaceAll('p>', 'td>') + lastColumn + '</tr>')
            });
            makeReadOnly();
            $wrapper.data('set', data['set']);
            $wrapper.data('end', data['end']);
            if (!data['end']) {
                $wrapper.attr('disabled', false);
            }

            // render well chart
            if ($manyToMany.attr('id') === 'stratigraphic_log' || $manyToMany.attr('id') === 'structure') {
                wellChart()
            }

            // render chart
            if (chart) {
                chart.refetchData()
            }
        },
        error: function (error, textStatus, request) {
            $wrapper.attr('disabled', false);
        }
    });
}

$(document).ready(function () {
    $('.add-new-many-to-many').click(function () {
        let $table = $(this).closest('.many-to-many').find('table');
        let template = $(this).closest('.many-to-many').find('template')[0];
        addNewRow($table, template)
    })
    const $tableWrapper =  $('.table-wrapper');
    $tableWrapper.on('scroll', function () {
        if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
            if (!$(this).attr('disabled')) {
                const set = $(this).data('set');
                fetchManyToMany($(this), set)
            }
        }
    })
    $tableWrapper.each(function () {
        fetchManyToMany($(this), 1)
    });
})

function toggleFullScreen(element) {
    let $manyToMany = $(element).closest('.many-to-many');
    $manyToMany.toggleClass('fullscreen');
    if ($manyToMany.hasClass('fullscreen')) {
        let $wrapper = $manyToMany.find('.table-wrapper');
        const set = $wrapper.data('set');
        fetchManyToMany($wrapper, set)
    }
}