// main.js — shared site scripts

(function () {
    'use strict';

    // ---------------------------------------------------------------
    // Theme toggle (light / dark)
    // Persistence: localStorage 'spendly-theme' ('light' | 'dark')
    // Fallback: prefers-color-scheme media query
    // ---------------------------------------------------------------

    var STORAGE_KEY = 'spendly-theme';

    function getStoredTheme() {
        try {
            return localStorage.getItem(STORAGE_KEY);
        } catch (e) {
            return null;
        }
    }

    function storeTheme(theme) {
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {
            // localStorage unavailable — preference won't persist this session
        }
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        var buttons = document.querySelectorAll('[data-theme-toggle]');
        buttons.forEach(function (btn) {
            btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
        });
    }

    function currentTheme() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }

    function toggleTheme() {
        var next = currentTheme() === 'dark' ? 'light' : 'dark';
        applyTheme(next);
        storeTheme(next);
    }

    // Apply on click for any toggle button rendered in the page
    document.addEventListener('click', function (e) {
        var target = e.target.closest('[data-theme-toggle]');
        if (!target) return;
        e.preventDefault();
        toggleTheme();
    });

    // Keep the toggle state in sync if the user hasn't picked manually
    // and the OS-level preference changes.
    var mql = window.matchMedia('(prefers-color-scheme: dark)');
    var handleSystemChange = function (e) {
        if (getStoredTheme()) return; // user override wins
        applyTheme(e.matches ? 'dark' : 'light');
    };
    if (mql.addEventListener) {
        mql.addEventListener('change', handleSystemChange);
    } else if (mql.addListener) {
        // Safari < 14
        mql.addListener(handleSystemChange);
    }

    // Sync aria-pressed on initial paint (in case multiple buttons exist)
    applyTheme(currentTheme());
})();
