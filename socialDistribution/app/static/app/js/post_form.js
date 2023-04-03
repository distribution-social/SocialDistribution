$(document).ready(function() {
    var receiversField = $('#id_receivers').closest('.form-group');
    var visibilityField = $('#id_visibility');
    
    function toggleReceiversField() {
        if (visibilityField.val() === 'PRIVATE') {
            receiversField.show();
        } else {
            receiversField.hide();
        }
    }
    
    // Hide the receivers field initially if the visibility is not PRIVATE
    toggleReceiversField();
    
    // Show or hide the receivers field whenever the visibility is changed
    visibilityField.on('change', function() {
        toggleReceiversField();
    });
});