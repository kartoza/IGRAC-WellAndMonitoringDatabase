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

function readURL(input, $preview) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $preview.attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]); // convert to base64 string
        $(this).data('value', input.files[0].name)
    }
}

$(document).ready(function () {
    // SCROLL EVENT
    // Cache selectors
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

    const turnOnElement = function ($element) {
        let id = $element.attr('id');
        if (lastId !== id) {
            lastId = id;
            // Set/remove active class
            $('.nav').removeClass("active");
            let activateButton = menuItems.filter("[href='#" + id + "']").parent();
            activateButton.closest('ul').closest('li').find('div.nav').addClass("active")
            activateButton.addClass("active");

        }
    }
    // Bind to scroll
    $singlePage.scroll(function () {
        if (scrollOnClick) {
            return;
        }

        // check element based on position
        let $element = null;
        $($scrollItems.get().reverse()).each(function (index) {
            if ($(this).position().top <= 0) {
                $element = $(this);
                return false;
            }
        });
        turnOnElement($element)
    });

    $scrollItems.mouseenter(function (e) {
        turnOnElement($(this))
    });

    $('#id_valid_from').change(function () {
        formValidator.form();
    })
    $('#id_valid_until').change(function () {
        formValidator.form();
    })
})

function chartTableToggle(elm, dataID) {
    $(elm).toggleClass('fa-line-chart fa-table');
    if ($(elm).hasClass('fa-table')) {
        $(`#${dataID}_table`).hide();
        $(`#${dataID}_chart`).show();

        let measurement = measurementCharts[dataID];
        if (measurement) {
            measurement.refetchData();
        }
    } else {
        $(`#${dataID}_table`).show();
        $(`#${dataID}_chart`).hide();
    }
}

function makeReadOnly() {
    if (readOnly) {
        $('#form input[type=file]').closest('.inputfile').addClass('disabled')
        $('#form input, textarea').not(".read-only").after(function () {
            if ($(this).hasClass('read-only')) {
                return ''
            }
            $(this).addClass('read-only');
            const style = $(this).prop("hidden") || $(this).attr('type') === 'hidden' ? 'display:none!important' : '';
            let value = $(this).val()
            if ($(this).attr('type') === 'checkbox') {
                value = $(this).attr('checked') ? 'Public' : 'Private';
            }
            return `<span name="${$(this).prop("name")}" class="input-data" style="${style}">${value}</span>`;
        });
        $('#form input, textarea').hide();
        $('#form select').not(".read-only").after(function () {
            if ($(this).hasClass('read-only') || $(this).hasClass('measurement-chart-nav')) {
                return ''
            }
            $(this).addClass('read-only');
            const style = $(this).prop("hidden") || $(this).attr('type') === 'hidden' ? 'display:none!important' : '';
            let value = $(this).data('value') !== 'None' ? $(this).find("option:selected").text() : '';
            if (value.includes('---')) {
                value = ''
            }
            return `<span name="${$(this).prop("name")}" class="input-data" style="${style}">${value}</span>`;
        });
        $('#form select').not('.measurement-chart-nav').hide();

        // this is for permissions section
        $('#id_public, .public-input').hide();
        if (!$('#id_public').attr('checked')) {
            $('.public-indicator span').html('Not anyone')
        }
        $('#id_downloadable, .downloadable-input').hide();
        if (!$('#id_downloadable').attr('checked')) {
            $('.downloadable-indicator span').html('Not downloadable')
        }
        if ($('#id_affiliate_organisations .multivalue-selection div').length === 0) {
            $('#id_affiliate_organisations').hide()
            $('#id_affiliate_organisations-label').hide()
        } else {
            $('#id_affiliate_organisations .multivalue-selection span').remove();
            $('#id_affiliate_organisations .input-data').hide();
        }
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
    colors = [colour, '#606060', '#994C00', '#808080', '#330000', '#A2A09F'];
    return chroma.average(colors).hex();
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

function sort_unique(arr) {
    if (arr.length === 0) return arr;
    arr = arr.sort(function (a, b) {
        return a * 1 - b * 1;
    });
    var ret = [arr[0]];
    for (var i = 1; i < arr.length; i++) { //Start loop at 1: arr[0] can never be a duplicate
        if (arr[i - 1] !== arr[i]) {
            ret.push(arr[i]);
        }
    }
    return ret;
}