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

$(document).ready(function () {
    $('.add-new-many-to-many').click(function () {
        let $table = $(this).closest('.many-to-many').find('table');
        let template = $(this).closest('.many-to-many').find('template')[0];
        addNewRow($table, template)
    })

    $('.table-wrapper').on('scroll', function () {
        if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
            if (!$(this).find('table').data('disabled')) {
                $(this).find('table').data('disabled', true)
            }
        }
    })
    $('.table-wrapper').each(function (index) {
        let $table = $(this).find('table');
        console.log($table.data('model'))
    });

}) 