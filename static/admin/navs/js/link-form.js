(function() {
    'use strict';

    function updateFormFields() {
        const link_types = document.querySelectorAll('input[name="link_type"]');

        const id_page  = document.getElementById('id_page');
        const id_route = document.getElementById('id_url_name');
        const id_url   = document.getElementById('id_url');

        const field_page  = id_page  ? (id_page.closest('.form-group')  || id_page.closest('.field-page')) : '';
        const field_route = id_route ? (id_route.closest('.form-group') || id_route.closest('.field-url_name')) : '';
        const field_url   = id_url   ? (id_url.closest('.form-group')   || id_url.closest('.field-url')) : '';

        function toggleFields(link_type) {
            // Hide all type-specific fields
            if (field_page) field_page.style.display = 'none';
            if (field_route) field_route.style.display = 'none';
            if (field_url) field_url.style.display = 'none';

            // Show only the selected type's field
            if (link_type === 'page' && field_page) {
                field_page.style.display = 'block';
            } else if (link_type === 'url_name' && field_route) {
                field_route.style.display = 'block';
            } else if (link_type === 'url' && field_url) {
                field_url.style.display = 'block';
            }
        }

        // Add event listeners to radio buttons
        link_types.forEach(type => {
            type.addEventListener('change', function() {
                toggleFields(this.value);
            });
        });

        // Initialize on page load
        const link_checked = document.querySelector('input[name="link_type"]:checked');
        if (link_checked) {
            toggleFields(link_checked.value);
        }
    }

    // Run when DOM is ready
    document.addEventListener('DOMContentLoaded', updateFormFields);
})();
