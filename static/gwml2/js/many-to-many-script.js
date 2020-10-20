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

/** add new row, and put data if presented **/
function addNewRow($table, template, data) {
    $table.append(template.content.cloneNode(true));

    let $inputTime = $table.find('tr').last().find('input[name ="time"]');
    $inputTime.attr('autocomplete', 'off');
    $inputTime.datetimepicker({
        formatTime: 'H:i',
        format: 'Y-m-d H:i',
    });
}

function addRowData($table, html) {
    $table.append(html);

    let $inputTime = $table.find('tr').last().find('input[name ="time"]');
    $inputTime.attr('autocomplete', 'off');
    $inputTime.datetimepicker({
        formatTime: 'H:i',
        format: 'Y-m-d H:i',
    });
}

$(document).ready(function () {
    $('.add-new-many-to-many').click(function () {
        let $table = $(this).closest('.many-to-many').find('table');
        let template = $(this).closest('.many-to-many').find('template')[0];
        addNewRow($table, template)
    })

    function fetchManyToMany($element, set) {
        let $wrapper = $element;
        let $table = $element.find('table');
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
                $wrapper.prop('disabled', false);
            },
            error: function (error, textStatus, request) {
                console.log(error)
            }
        });
    }

    $('.table-wrapper').on('scroll', function () {
        if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
            if (!$(this).prop('disabled')) {
                $(this).prop('disabled', true);
                const set = $(this).data('set');
                fetchManyToMany($(this), set)
            }
        }
    })
    $('.table-wrapper').each(function () {
        fetchManyToMany($(this), 1)
    });

}) 