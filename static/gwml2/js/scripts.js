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
    $('.nav li').removeClass('active')
    $('.form-title span').html($(this).find('span').text())
})

function fileSelectionChanged(element) {
    var fileName = '';
    if ($(element).val()) {
        fileName = $(element).val().split('\\').pop();
    }
    $(element).closest('div').find('span').html(fileName)
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