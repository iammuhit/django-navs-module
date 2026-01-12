(function($) {
    'use strict';
    
    $(document).ready(function() {
        const $results = $('#result_list');

        $results
            .find('thead tr th.column-action_buttons')
            .removeClass('column-action_buttons')
            .addClass('column-actions');
        
        $results
            .find('tbody tr td.field-action_buttons')
            .removeClass('field-action_buttons')
            .addClass('field-actions');
    });
})(django.jQuery);
