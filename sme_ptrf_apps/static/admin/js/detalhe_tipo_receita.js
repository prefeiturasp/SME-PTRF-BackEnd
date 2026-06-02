(function () {
    'use strict';
    document.addEventListener('DOMContentLoaded', function () {
        var recursoSelect = document.getElementById('id_recurso');
        if (!recursoSelect) return;

        recursoSelect.addEventListener('change', function () {
            var url = new URL(window.location.href);
            if (this.value) {
                url.searchParams.set('recurso', this.value);
            } else {
                url.searchParams.delete('recurso');
            }
            window.location.href = url.toString();
        });
    });
}());
