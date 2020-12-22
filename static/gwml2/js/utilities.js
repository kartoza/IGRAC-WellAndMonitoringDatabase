/** Return top and ground water surfaces of well
 * It will return in json
 * {
 *     top_borehole : '',
 *     ground_surface : ''
 * }
 */
function getTopGroundSurfaceWell(unit_to) {
    let top_borehole_elevation_unit = valElmt($('*[name^="top_borehole_elevation_unit"]'));
    let ground_surface_elevation_unit = valElmt($('*[name^="ground_surface_elevation_unit"]'));
    return {
        top_borehole: valElmt($('*[name^="top_borehole_elevation_value"]')) ? unitConvert(
            top_borehole_elevation_unit, unit_to, valElmt($('*[name^="top_borehole_elevation_value"]'))) : null,
        ground_surface: valElmt($('*[name^="ground_surface_elevation_value"]')) ? unitConvert(
            ground_surface_elevation_unit, unit_to, valElmt($('*[name^="ground_surface_elevation_value"]'))) : null
    }
}

/** Return value of quantity input
 */
function getQuantityInputValue($element, unit_to) {
    let value = $element.find('.quantity-value').val();
    let unit = $element.find('.quantity-unit').val();
    if (value === undefined || value === null) {
        return value
    }
    return unitConvert(unit, unit_to, value);
}

/** Return check
 *
 */
function checkFileIsAccepted(elm) {
    let names = elm.files[0].name.split('.');
    let accepts = $(elm).attr('accept');
    if (names.length > 1 && accepts.includes(names[1])) {
        return true
    } else {
        return false
    }
}