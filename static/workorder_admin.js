(function($) {
    $(document).ready(function() {
        $('#id_dsl_card').change(function() {
            const cardId = $(this).val();
            const portSelect = $('#id_dsl_port');

            if (cardId) {
                $.ajax({
                    url: '/admin/get_ports_for_card/',  // Update to your actual endpoint
                    data: { dsl_card: cardId },
                    success: function(data) {
                        portSelect.empty();
                        data.forEach(function(port) {
                            portSelect.append(new Option(port.port_number, port.id));
                        });
                    }
                });
            } else {
                portSelect.empty();
            }
        });
    });
})(django.jQuery);
