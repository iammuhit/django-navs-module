(function($) {
    $(document).ready(function() {
        var $results = $('#result_list');

        // Get CSRF Token
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let idx = 0; idx < cookies.length; idx++) {
                    const cookie = cookies[idx].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        if ($results.length) {
            // Make table rows sortable
            $results.find('tbody').sortable({
                handle: $(this).find('tr'),
                cursor: 'move',
                opacity: 0.7,
                update: function(event, ui) {
                    var items = [];
                    $(this).find('tr').each(function(index) {
                        var id = $(this).find('input[name="_selected_action"]').val();
                        if (id) {
                            items.push({
                                id: id,
                                order: index
                            });
                        }
                    });
                    
                    // Send update to server
                    $.ajax({
                        url: '/admin/navs/link/order/',
                        method: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({items: items}),
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        success: function() {
                            // Update order column visually if displayed
                            $results.find('tbody tr').each(function(index) {
                                $(this).find('input[name*="order"]').val(index);
                            });
                        },
                        error: function(xhr, status, error) {
                            // console.error('Error:', error);
                            // console.error('Response:', xhr.responseText);
                        }
                    });
                }
            });
            
            // Add visual indicator that rows are draggable
            $results.find('tbody tr').css('cursor', 'move');
        }
    });
})(django.jQuery);
