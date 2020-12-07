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

function parameterChanged($inputParameter, $inputUnit) {
    let units = parameters[$inputParameter.val()] || [];
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
            if (val && val === $(this).attr('value')) {
                $inputUnit.val('')
            }
        }
    });
}

function initRowData($row) {
    let $inputTime = $row.find('input[name="time"]');
    $inputTime.attr('autocomplete', 'off');
    $inputTime.datetimepicker({
        formatTime: 'H:i',
        format: 'Y-m-d H:i',
    });

    // parameters
    let $inputParameter = $row.find('select[name="parameter"]');
    if ($inputParameter.length > 0) {
        let $inputUnit = $row.find('select[name="value_unit"]');
        $inputParameter.change(function () {
            parameterChanged($inputParameter, $inputUnit);
        });
        $inputParameter.trigger('change')
    }
    $row.find('input,select,textarea').change(function () {
        $row.addClass('updated')
    });

    // parameters
    let $detailInput = $row.find('input[name="info"]');
    if ($detailInput.length > 0) {
        $detailInput.replaceWith(`<i class="fa fa-info-circle" aria-hidden="true" title="${$detailInput.val()}"></i>`)
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
            if (!data['end']) {
                $wrapper.attr('disabled', false);
            }

            // render well chart
            if ($manyToMany.attr('id') === 'stratigraphic_log' || $manyToMany.attr('id') === 'structure') {
                wellChart()
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
    $('.add-new-many-to-many-csv-input').change(function () {
        let $table = $(this).closest('.many-to-many').find('table');
        let template = $(this).closest('.many-to-many').find('template')[0];
        if (this.files && this.files[0]) {
            let _file = this.files[0];
            let reader = new FileReader();
            reader.addEventListener('load', function (e) {
                let csvdata = e.target.result;
                let data = parseCSV(csvdata); // calling function for parse csv data
                for (let i = 0; i < data.length; i++) {
                    addNewRow($table, template, data[i])
                }
            });

            reader.readAsBinaryString(_file);
        }
    });

    $('.table-wrapper').on('scroll', function () {
        if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
            if (!$(this).attr('disabled')) {
                const set = $(this).data('set');
                fetchManyToMany($(this), set)
            }
        }
    })
    $('.table-wrapper').each(function () {
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