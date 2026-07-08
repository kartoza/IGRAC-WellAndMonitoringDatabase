(function ($) {
  function formatNumber(value) {
    return Number(value || 0).toLocaleString('en-US');
  }

  function parseNumber(text) {
    return Number(String(text || '0').replace(/,/g, '')) || 0;
  }

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function animateStat($cell, from, to, duration) {
    let startTime = null;

    if (from === to) {
      $cell.text(formatNumber(to));
      return;
    }

    function step(timestamp) {
      if (startTime === null) {
        startTime = timestamp;
      }
      let progress = Math.min(
        (timestamp - startTime) / duration, 1
      );
      let eased = easeOutCubic(progress);
      let current = Math.round(from + (to - from) * eased);
      $cell.text(formatNumber(current));
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    }

    window.requestAnimationFrame(step);
  }

  window.WellDashboardUtils = {
    formatNumber: formatNumber,
    parseNumber: parseNumber,
    easeOutCubic: easeOutCubic,
    animateStat: animateStat
  };
})(jQuery);