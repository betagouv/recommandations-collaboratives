function access_update_app(url) {
    return {
        url: url,
        isCopied: false,
        clipboardCopy: function() {
            navigator.clipboard.writeText(url).then(function () {
                this.isCopied = true;
                this.$refs.button.blur();
            }.bind(this));
        }
    }
}