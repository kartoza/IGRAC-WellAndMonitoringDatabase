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

    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('#photo-preview').attr('src', e.target.result);
            }
            reader.readAsDataURL(input.files[0]); // convert to base64 string
        }
    }


    $("#id_photo").change(function () {
        readURL(this);
    });

    // Cache selectors
    var lastId,
        topMenu = $(".inner-navigation"),
        //topMenuHeight = topMenu.outerHeight()+15,
        // All list items
        menuItems = topMenu.find("a"),
        // Anchors corresponding to menu items
        scrollItems = menuItems.map(function () {
            var item = $($(this).attr("href"));
            if (item.length) {
                return item;
            }
        });

    // Bind click handler to menu items
    // so we can get a fancy scroll animation
    menuItems.click(function (e) {
        $('.form-title span').html($(this).find('span').text());

        var href = $(this).attr("href"),
            offsetTop = href === "#" ? 0 : $(href).position().top + $('.singlepage').scrollTop() - 40;
        $('.singlepage').stop().animate({
            scrollTop: offsetTop
        }, 300);
        e.preventDefault();
    });

    // Bind to scroll
    $('.singlepage').scroll(function () {
        // Get container scroll position
        var fromTop = $(this).position().top + 60;

        // Get id of current scroll item
        var cur = scrollItems.map(function () {
            var cur = scrollItems.map(function () {
                if ($(this).position().top < fromTop)
                    return this;
            });
            // Get the id of the current element
            cur = cur[cur.length - 1];
            var id = cur && cur.length ? cur[0].id : "";

            if (lastId !== id) {
                lastId = id;
                // Set/remove active class
                menuItems
                    .parent().removeClass("active")
                    .end().filter("[href='#" + id + "']").parent().addClass("active");
                $('.form-title span').html(menuItems.filter("[href='#" + id + "']").find('span').text());

            }
        });
    });
})

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