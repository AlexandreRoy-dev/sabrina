(function() {
    var COOKIE_NAME = 'cookie_consent';
    var COOKIE_MAX_AGE = 365 * 24 * 60 * 60; // 1 year in seconds

    function setCookie(value) {
        document.cookie = COOKIE_NAME + '=' + encodeURIComponent(value) + '; path=/; max-age=' + COOKIE_MAX_AGE + '; SameSite=Lax';
    }

    function getCookie() {
        var match = document.cookie.match(new RegExp('(^| )' + COOKIE_NAME + '=([^;]+)'));
        return match ? decodeURIComponent(match[2]) : null;
    }

    function hideBanner() {
        var banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.classList.add('opacity-0', 'translate-y-full', 'pointer-events-none');
            setTimeout(function() { banner.style.display = 'none'; }, 300);
        }
    }

    function init() {
        var banner = document.getElementById('cookie-consent-banner');
        if (!banner) return;
        if (getCookie()) {
            banner.style.display = 'none';
            return;
        }
        banner.style.display = 'block';
        var acceptBtn = document.getElementById('cookie-consent-accept');
        var refuseBtn = document.getElementById('cookie-consent-refuse');
        if (acceptBtn) {
            acceptBtn.addEventListener('click', function() {
                setCookie('accepted');
                hideBanner();
            });
        }
        if (refuseBtn) {
            refuseBtn.addEventListener('click', function() {
                setCookie('refused');
                hideBanner();
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
