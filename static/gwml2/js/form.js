/** This check validation for ground surface and top of borehole
 */

/** Latitude and longitude check
 */
$.validator.addMethod(
    "latitudeValidation",
    function (value, element) {
        return (-90 <= parseInt(value) && parseInt(value) <= 90)
    },
    "Please enter a value comprised between -90 and 90"
);
$.validator.addMethod(
    "longitudeValidation",
    function (value, element) {
        return (-180 <= parseInt(value) && parseInt(value) <= 180)
    },
    "Please enter a value comprised between -180 and 180"
);

/** Validation for groundsurface elevation
 */
$.validator.addMethod(
    "groundSurfaceValidation",
    function (value, element) {
        const wellElevation = getTopGroundSurfaceWell('m')
        const top_borehole = wellElevation['top_borehole'];
        const ground_surface = wellElevation['ground_surface'];
        if (top_borehole !== null && ground_surface !== null) {
            if (ground_surface <= top_borehole) {
                const $groundwater = $('#id_ground_surface_elevation_value');
                const $topBorehole = $('#id_top_borehole_elevation_value');
                // if it is ok, make everything valid
                $groundwater.closest('.quantity-input').find('.quantity-value').removeClass('error').addClass('valid')
                $topBorehole.closest('.quantity-input').find('.quantity-value').removeClass('error').addClass('valid')
                $groundwater.closest('.quantity-input').find('.error').hide()
                $topBorehole.closest('.quantity-input').find('.error').hide()
                return true
            } else {
                return false
            }
        }
        return true;
    },
    "Ground surface elevation should be lower than Top of well elevation"
);

/** This check validation for top and bottom depth
 */
$.validator.addMethod(
    "bottomDepthValidation",
    function (value, element) {
        const $row = $(element).closest('tr');
        if ($row.length === 0) {
            return true
        }
        const $topDepth = $row.find('#id_top_depth_id');
        const $bottomDepth = $row.find('#id_bottom_depth_id');
        const topDepth = getQuantityInputValue($topDepth.closest('.quantity-input'), 'm');
        const bottomDepth = getQuantityInputValue($bottomDepth.closest('.quantity-input'), 'm');
        if (topDepth !== null && bottomDepth !== null) {
            if (bottomDepth >= topDepth) {
                // if it is ok, make everything valid
                $topDepth.closest('.quantity-input').find('.quantity-value').removeClass('error').addClass('valid')
                $bottomDepth.closest('.quantity-input').find('.quantity-value').removeClass('error').addClass('valid')
                $topDepth.closest('.quantity-input').find('.error').hide()
                $bottomDepth.closest('.quantity-input').find('.error').hide()
                return true
            } else {
                return false
            }
        }
        return true;
    },
    "Top depth value should be lower than bottom depth value"
);
/** This check validation for license
 */
$.validator.addMethod(
    "validFromValidation",
    function (value, element) {
        const $validFrom = $('#id_valid_from');
        const $validUntil = $('#id_valid_until');
        if ($validUntil.val() !== null && $validFrom.val() !== null) {
            return $validFrom.val() <= $validUntil.val()
        }
        return true;
    },
    "Valid from should be before valid until"
);

/** This check validation for can't be more than total depth
 */
$.validator.addMethod(
    "checkWithTotalDepth",
    function (value, element) {
        // we keep into groundwater
        let total_depth = getQuantityInputValue($('#id_total_depth'), 'm')
        let total_depth_elevation = referenceElevations[$('#geology #id_reference_elevation').val()]
        if (total_depth === undefined || total_depth === null || total_depth_elevation === null) {
            return true
        }

        let topGround = getTopGroundSurfaceWell('m');
        const top_borehole = topGround['top_borehole'];
        const ground_surface = topGround['ground_surface'];
        let different = 0;
        if (top_borehole && ground_surface) {
            different = top_borehole - ground_surface;
        }
        if (total_depth_elevation === ELEVATION_TOPBOREHOLE) {
            total_depth = total_depth - different
        }
        let referenceElevation = referenceElevations[$(element).closest('tr').find('#id_reference_elevation').val()]
        value = parseInt(value)
        if (referenceElevation === ELEVATION_TOPBOREHOLE) {
            value = value - different
        }
        if (value > total_depth) {
            return false
        } else {
            return true
        }

    },
    "The depth should be lower than total depth"
);

/** This check validation for photo
 */
$.validator.addMethod(
    "validPhotoExtension",
    function (value, element) {
        return checkFileIsAccepted(element);
    },
    "Photo is not valid file"
);
$('#form').submit(function () {
    return false;
})

const formValidator = $('#form').validate({
    errorElement: 'div',
    /** Handle event when there is invalid event
     */
    rules: {
        latitude: {
            latitudeValidation: true
        },
        longitude: {
            longitudeValidation: true
        },
        ground_surface_elevation_value: {
            groundSurfaceValidation: true
        },
        top_borehole_elevation_value: {
            groundSurfaceValidation: true
        },
        top_depth_value: {
            checkWithTotalDepth: true,
            bottomDepthValidation: true
        },
        bottom_depth_value: {
            checkWithTotalDepth: true,
            bottomDepthValidation: true
        },
        depth_value: {
            checkWithTotalDepth: true
        },
        valid_from: {
            validFromValidation: true
        },
        photo: {
            validPhotoExtension: true
        }
    },
    showErrors: function (errorMap, errorList) {
        this.defaultShowErrors();
        $('div.error').click(function () {
            $(this).hide()
        })
    },
    invalidHandler: function (event, validator) {
        $('.navigation a').removeClass('error')
        if (validator.invalid) {
            setTimeout(function () {
                $('div.error:visible').each(function () {
                    $("a[href$='#" + $(this).closest('.page-section').attr('id') + "']").addClass('error')
                })
            }, 100);
        }
    },
    /** Submit form
     */
    submitHandler: function (form, event) {
        $('.navigation a').removeClass('error')
        event.preventDefault();
        $('#form-submit').attr("disabled", true);
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
                window.location.href = data;
            },
            error: function (error) {
                $('#form-submit').attr("disabled", false);
                alert(error['responseText'])
            },
            data: formData
        });
    }
});