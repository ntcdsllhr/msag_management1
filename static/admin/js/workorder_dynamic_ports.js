(function($) {
    $(document).ready(function() {
        // Watch changes to the MSAG dropdown
        $('#id_msag').change(function() {
            var msagId = $(this).val();  // Get selected MSAG ID
            var portSelect = $('#id_dsl_port');  // DSL port dropdown

            if (msagId) {
                // Make an AJAX request to fetch available ports
                $.ajax({
                    url: '/admin/get_available_ports/',  // Endpoint to fetch ports
                    data: {
                        msag_id: msagId
                    },
                    success: function(data) {
                        // Clear and populate the DSL port dropdown
                        portSelect.empty();
                        portSelect.append($('<option>', { value: '', text: '---------'}));  // Default blank option
                        $.each(data.ports, function(index, port) {
                            portSelect.append($('<option>', { value: port.id, text: port.port_number }));
                        });
                    },
                    error: function() {
                        alert('Error fetching available ports.');
                    }
                });
            } else {
                // Clear the DSL port dropdown if no MSAG is selected
                portSelect.empty();
                portSelect.append($('<option>', { value: '', text: '---------'}));
            }
        });
    });
})(django.jQuery);
