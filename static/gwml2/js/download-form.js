$(document).ready(function () {
  // Kept in sync with `DownloadRequestBaseForm.OTHERS_VALUE` in
  // gwml2/forms/download_request.py.
  const OTHERS_VALUE = '__others__';

  const $wrapper = $('#id_organization_types');
  const $select = $wrapper.find('select');
  const placeholder = 'Select an organization type or more.';

  $select.select2({
    placeholder: placeholder,
    allowClear: true,
    minimumResultsForSearch: -1
  });

  const $otherInput = $(
    '<input type="text" class="form-control" ' +
    'id="id_organization_types_other" ' +
    'placeholder="Please specify the organization type" ' +
    'style="margin-top: 8px; display: none;">'
  );
  $wrapper.append($otherInput);

  $otherInput.on('input', function () {
    this.setCustomValidity('');
  });

  const $initialOther = $('#id_organization_types_other_initial');
  if ($initialOther.length && $initialOther.val()) {
    $otherInput.val($initialOther.val());
    // The rendered <select> won't have "Others" marked as selected when
    // the custom value came from raw (bound) POST data instead of the
    // form's initial data, so force it here based on the hidden field.
    $select.find(`option[value="${OTHERS_VALUE}"]`).prop('selected', true);
    $select.trigger('change');
  }

  function toggleOtherInput() {
    const values = $select.val() || [];
    if (values.indexOf(OTHERS_VALUE) !== -1) {
      $otherInput.show().prop('required', true);
    } else {
      $otherInput.hide().prop('required', false);
      $otherInput.val('');
      $otherInput[0].setCustomValidity('');
    }
  }

  $select.on('change', toggleOtherInput);
  toggleOtherInput();

  const $form = $select.closest('form');
  $form.on('submit', function (e) {
    const values = $select.val() || [];
    if (values.indexOf(OTHERS_VALUE) === -1) {
      return;
    }

    const customValue = $otherInput.val().trim();
    if (!customValue) {
      e.preventDefault();
      $otherInput[0].setCustomValidity('Please specify the organization type.');
      $otherInput[0].reportValidity();
      return;
    }

    // Replace the sentinel selection with the real, user-specified value(s).
    $select.find(`option[value="${OTHERS_VALUE}"]`).prop('selected', false);
    customValue.split(',').map(v => v.trim()).filter(Boolean).forEach(function (v) {
      const $existing = $select.find('option').filter(function () {
        return $(this).val() === v;
      });
      if ($existing.length) {
        $existing.prop('selected', true);
      } else {
        $select.append(new Option(v, v, true, true));
      }
    });
  });
});
