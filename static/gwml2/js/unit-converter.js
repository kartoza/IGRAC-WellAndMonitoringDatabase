function unitConvert(unitFrom, unitTo, value) {
    value = parseFloat(value)
    // unit from
    switch (unitFrom) {
        // LENGTH
        case 'ft':
            switch (unitTo) {
                case 'm':
                    return Math.round(value / 3.281);
                case 'cm':
                    return Math.round(value * 100 / 3.281);
            }
            break;
        case 'm':
            switch (unitTo) {
                case 'ft':
                    return Math.round(value * 3.281);
                case 'cm':
                    return Math.round(value * 100);
            }
            break;
        case 'cm':
            switch (unitTo) {
                case 'ft':
                    return Math.round(value * 3.281 / 100);
                case 'm':
                    return Math.round(value / 100);
            }
            break;

        // TEMPERATURE
        case '°F':
            switch (unitTo) {
                case '°C':
                    return (value - 32) * 5 / 9
                case '°K':
                    return (value - 32) * 5 / 9 + 273.15
            }
            break;
        case '°C':
            switch (unitTo) {
                case '°F':
                    return (value * 9 / 5) + 32
                case '°K':
                    return value + 273.15
            }
            break;
        case '°K':
            switch (unitTo) {
                case '°F':
                    return (value - 273.15) * 9 / 5 + 32
                case '°K':
                    return value - 273.15
            }
            break;

        // MASS / VOLUME
        case 'mg/L':
            switch (unitTo) {
                case 'μg/L':
                    return value * 1000
                case 'ng/L':
                    return value * 1000 * 1000
            }
            break;
        case 'μg/L':
            switch (unitTo) {
                case 'mg/L':
                    return value / 1000
                case 'ng/L':
                    return value * 1000
            }
            break;
        case 'ng/L':
            switch (unitTo) {
                case 'mg/L':
                    return value / (1000 * 1000)
                case 'μg/L':
                    return value / 1000
            }
            break;
    }
    return value
}