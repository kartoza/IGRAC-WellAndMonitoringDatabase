function deleteRelation(elm) {
    /*** Deleting relation of many to many
     *
     * @type {boolean}
     */
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
    $inputUnit.find('option').each(function (index) {
        if (units.includes($(this).attr('value'))) {
            $(this).show();
        } else {
            $(this).hide();
            $(this).removeAttr('selected');
        }
    });
}

/** add new row, and put data if presented **/
function addNewRow($table, template, data) {
    $table.append(template.content.cloneNode(true));

    let $inputTime = $table.find('tr').last().find('input[name ="time"]');
    $inputTime.attr('autocomplete', 'off');
    $inputTime.datetimepicker({
        formatTime: 'H:i',
        format: 'Y-m-d H:i',
    });

    // parameters
    let $inputParameter = $table.find('tr').last().find('select[name="parameter"]');
    if ($inputParameter.length > 0) {
        let $inputUnit = $table.find('tr').last().find('select[name="value_unit"]');
        $inputParameter.change(function () {
            parameterChanged($inputParameter, $inputUnit);
        });
        $inputParameter.trigger('change')
    }
}

function addRowData($table, html) {
    $table.append(html);

    let $inputTime = $table.find('tr').last().find('input[name="time"]');
    $inputTime.attr('autocomplete', 'off');
    $inputTime.datetimepicker({
        formatTime: 'H:i',
        format: 'Y-m-d H:i',
    });

    // parameters
    let $inputParameter = $table.find('tr').last().find('select[name="parameter"]');
    if ($inputParameter.length > 0) {
        let $inputUnit = $table.find('tr').last().find('select[name="value_unit"]');
        $inputParameter.change(function () {
            parameterChanged($inputParameter, $inputUnit);
        });
        $inputParameter.trigger('change')
    }
}


function fetchManyToMany($element, set) {
    let $wrapper = $element;
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
        },
        error: function (error, textStatus, request) {
            $wrapper.attr('disabled', false);
        }
    });
}

$(document).ready(function () {
    $('.add-new-many-to-many').click(function () {
        let $table = $(this).closest('.many-to-many').find('table tbody');
        let template = $(this).closest('.many-to-many').find('template')[0];
        addNewRow($table, template)
    })

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