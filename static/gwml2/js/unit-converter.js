function unitConvert(unitFrom, unitTo, value) {
    if (value === undefined || value === null || value === '') {
        return value
    }

    value = parseFloat(value);
    const formula = unitsDict[unitFrom]?.to[unitTo];
    if (formula) {
        value = eval(formula.replace('x', value));
    } else {
        if (unitFrom && unitFrom !== unitTo) {
            return null;
        }
    }
    return value
}