import Alpine from 'alpinejs'

Alpine.data("PrintTaskResource", PrintTaskResource)

function PrintTaskResource() {
    return {
        handlePrintResourceIframe(event) {
            event.preventDefault();
            window.frames.focus();
            window.frames.print();
        }
    }
}

