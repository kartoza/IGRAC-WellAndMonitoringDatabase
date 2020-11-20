const chartColors = [
    "rgb(255, 99, 132)",
    "rgb(54, 162, 235)",
    "rgb(153, 102, 255)",
    "rgb(255, 205, 86)",
    "rgb(75, 192, 192)",
    "rgb(255, 159, 64)",
    "rgb(201, 203, 207)"
]
$('li.nav').click(function () {
    $('.nav').removeClass('active')
    $(this).closest('ul').closest('li').find('div.nav').addClass("active")
    $('.form-title span').html($(this).find('span').text())
})

function fileSelectionChanged(element) {
    var fileName = '';
    if ($(element).val()) {
        fileName = $(element).val().split('\\').pop();
    }
    $(element).closest('div').find('span').html(fileName)
}

function getBottom($el, $wrapper) {
    return $el.position().top + $el.outerHeight(true) - $wrapper.outerHeight()
}

$(document).ready(function () {

    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('.photo-preview').attr('src', e.target.result);
            }
            reader.readAsDataURL(input.files[0]); // convert to base64 string
        }
    }


    $("#id_photo").change(function () {
        readURL(this);
    });

    // SCROLL EVENT
    // Cache selectors
    let $singleContent = $('#single-content');
    let $singlePage = $('.singlepage');
    const $scrollItems = $('.page-section');
    var lastId,
        topMenu = $(".inner-navigation"),
        //topMenuHeight = topMenu.outerHeight()+15,
        // All list items
        menuItems = topMenu.find("a");
    // Bind click handler to menu items
    // so we can get a fancy scroll animation
    let scrollOnClick = false;
    menuItems.click(function (e) {
        scrollOnClick = true;
        $('.form-title span').html($(this).find('span').text());
        var href = $(this).attr("href"),
            offsetTop = href === "#" ? 0 : $(href).position().top + $singlePage.scrollTop();
        $singlePage.stop().animate({
            scrollTop: offsetTop
        }, 300, function () {
            scrollOnClick = false;
        });
        e.preventDefault();
    });
    $singlePage.bind('mousewheel', function (e) {
        scrollOnClick = false;
    });
    // Bind to scroll
    $singlePage.scroll(function () {
        if (scrollOnClick) {
            return;
        }
        // Get container scroll position
        let top = $singleContent.position().top;

        // check element based on position
        let $element = null;
        $($scrollItems.get().reverse()).each(function (index) {
            if ($(this).position().top <= 0) {
                $element = $(this);
                return false;
            }
        });
        let id = $element.attr('id');
        if (lastId !== id) {
            lastId = id;
            // Set/remove active class
            $('.nav').removeClass("active");
            let activateButton = menuItems.filter("[href='#" + id + "']").parent();
            activateButton.closest('ul').closest('li').find('div.nav').addClass("active")
            activateButton.addClass("active");
            // $('.form-title span').html(menuItems.filter("[href='#" + id + "']").find('span').text());

        }
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

function makeReadOnly() {
    if (readOnly) {
        $('#form input[type=file]').closest('.inputfile').addClass('disabled')
        $('#form input, textarea').replaceWith(function () {
            const style = $(this).prop("hidden") || $(this).attr('type') === 'hidden' ? 'display:none!important' : '';
            return `<span name="${$(this).prop("name")}" class="input-data" style="${style}">${$(this).val()}</span>`;
        });
        $('#form select').replaceWith(function () {
            const style = $(this).prop("hidden") || $(this).attr('type') === 'hidden' ? 'display:none!important' : '';
            let value = $(this).data('value') !== 'None' ? $(this).find("option:selected").text() : '';
            if (value === '---------') {
                value = ''
            }
            return `<span name="${$(this).prop("name")}" class="input-data" style="${style}">${value}</span>`;
        });
    }
}

String.prototype.replaceAll = function (search, replacement) {
    let target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
}

const stringToColour = function (str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    let colour = '#';
    for (let i = 0; i < 2; i++) {
        let value = (hash >> (i * 8)) & 0xFF;
        colour += ('00' + value.toString(16)).substr(-2);
    }
    colour += '00'
    return colour;
}

const feetToMeter = function (value) {
    return Math.round(parseFloat(value) / 3.281)
}

function parseCSV(data) {
    let parsedata = [];
    let lines = data.split("\n");
    let headers = lines[0].split(",")
    for (let i = 1; i < lines.length - 1; i++) {
        let columns = lines[i].split(",");
        let columnData = {}
        for (let j = 0; j < columns.length; j++) {
            columnData[headers[j]] = columns[j]
        }
        parsedata.push(columnData)
    }
    console.log(parsedata)
    return parsedata;
}