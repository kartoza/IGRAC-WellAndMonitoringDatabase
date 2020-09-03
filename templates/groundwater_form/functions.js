const chartColors = [
    "rgb(255, 99, 132)",
    "rgb(54, 162, 235)",
    "rgb(153, 102, 255)",
    "rgb(255, 205, 86)",
    "rgb(75, 192, 192)",
    "rgb(255, 159, 64)",
    "rgb(201, 203, 207)"
]
$('.add-new-many-to-many').click(function () {
    let $table = $(this).closest('.many-to-many').find('table');
    let template = $(this).closest('.many-to-many').find('template')[0];
    $table.append(template.content.cloneNode(true));

    let $inputTime = $table.find('tr').last().find('input[name ="time"]');
    $inputTime.attr('autocomplete', 'off');
    $inputTime.datetimepicker({
        formatTime: 'H:i',
        format: 'Y-m-d H:i',
    });
})
$('li.nav').click(function () {
    $('.nav li').removeClass('active')
    $('.form-title span').html($(this).find('span').text())
})

$('#form').validate({
    errorElement: 'div',
    invalidHandler: function (event, validator) {
        $('.navigation a').removeClass('error')
        if (validator.invalid) {
            setTimeout(function () {
                $('div.error:visible').each(function () {
                    $("a[href$='#" + $(this).closest('.tab-pane').attr('id') + "']").addClass('error')
                })
            }, 100);
        }
    },
    submitHandler: function (form, event) {
        $('.navigation a').removeClass('error')
        event.preventDefault();
        let data = {}
        $.each(submitFunctions, function (form, value) {
            data[form] = value();
        });
        var formData = new FormData();
        $('input[type="file"]').each(function () {
            let file = $(this).get(0).files[0];
            if (file) {
                formData.append(file.name, file);
            }
        });
        formData.append('data', JSON.stringify(data));
        $.ajax({
            url: window.location,
            type: "POST",
            cache: false,
            contentType: false,
            processData: false,
            beforeSend: function (xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", $(this).find('*[name=csrfmiddlewaretoken]').val());
                }
            },
            success: function (data) {
                location.reload();
            },
            error: function (error) {
                alert(error['responseText'])
            },
            data: formData
        });
    }
});

function deleteRelation(elm) {
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

function fileSelectionChanged(element) {
    var fileName = '';
    if ($(element).val()) {
        fileName = $(element).val().split('\\').pop();
    }
    $(element).closest('div').find('span').html(fileName)
}

$(document).ready(function () {
    $(".select-2").select2({
        tags: true
    });
});

function chartTableToggle(elm, dataID) {
    $(elm).toggleClass('fa-line-chart fa-table');
    if ($(elm).hasClass('fa-table')) {
        $(`#${dataID}_table`).hide();
        $(`#${dataID}_chart`).show();
        chartFunctions[dataID]();
    } else {
        $(`#${dataID}_table`).show();
        $(`#${dataID}_chart`).hide();
    }
}