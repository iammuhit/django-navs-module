(function() {
    'use strict';

    const LINK_ADD_BASE_URL = '/admin/navs/link/add/';
    let currentUrl = new URL(window.location);

    function getPreservedParams() {
        const params = {};
        const urlParams = new URLSearchParams(window.location.search);
        const filters = urlParams.get('_changelist_filters');
        
        if (filters) {
            filters.split('&').forEach(pair => {
                if (pair.includes('=')) {
                    const [key, value] = pair.split('=', 2);
                    const cleanKey = key.replace(/__/g, '_');
                    params[cleanKey] = decodeURIComponent(value);
                }
            });
        }
        
        return params;
    }

    function showLinkTypeModal() {
        const modal = document.getElementById('modal-link-type');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    function hideLinkTypeModal() {
        const modal = document.getElementById('modal-link-type');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    function redirectToAddLink(menu_slug, link_type) {
        const url = new URL(LINK_ADD_BASE_URL, window.location.origin);
        url.searchParams.append('menu__slug', menu_slug);
        url.searchParams.append('link_type', link_type);
        
        // Preserve filters if present
        // currentUrl = new URL(window.location);
        // let filters = currentUrl.searchParams.get('_changelist_filters');
        // if (filters) {
        //     filters += encodeURI(`&link_type=${link_type}`);
        //     url.searchParams.append('_changelist_filters', filters);
        // }
        
        window.location.href = url.toString();
    }

    function initLinkTypeModal() {
        const modal = document.getElementById('modal-link-type');
        if (!modal) return;

        // Close button handler
        const closeBtn = modal.querySelector('.link-type-modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', hideLinkTypeModal);
        }

        // Modal background click handler
        modal.addEventListener('click', function(event) {
            if (event.target === this) {
                hideLinkTypeModal();
            }
        });

        // Link type option handlers
        const options = modal.querySelectorAll('.link-type-option');
        options.forEach(option => {
            option.addEventListener('click', function(event) {
                event.preventDefault();
                const params    = new URLSearchParams(window.location.search);
                const menu_slug = params.get('menu__slug');
                const link_type = this.getAttribute('data-type');
                redirectToAddLink(menu_slug, link_type);
            });
        });
    }

    function interceptAddLinkButton() {
        const observer = new MutationObserver(function(mutations) {
            const addButtons = document.querySelectorAll('a.addlink[href*="/navs/link/add/"]');
            addButtons.forEach(addButton => {
                // if (addButton && !addButton.dataset.intercepted) {
                //     addButton.dataset.intercepted = 'true';
                if (addButton) {
                    addButton.addEventListener('click', function(event) {
                        // Check if this is specifically for adding a link (not for inline)
                        if (this.href.includes('/navs/link/add/')) {
                            event.preventDefault();
                            currentUrl = new URL(this.href);
                            showLinkTypeModal();
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    }

    function updateFormFieldsBasedOnType() {
        const params = new URLSearchParams(window.location.search);
        const linkType = params.get('link_type');

        if (linkType) {
            // Remove the query parameter from URL
            // window.history.replaceState({}, document.title, window.location.pathname);
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        initLinkTypeModal();
        interceptAddLinkButton();
        updateFormFieldsBasedOnType();
    });
})();
