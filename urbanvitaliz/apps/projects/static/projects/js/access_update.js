function access_update_app(url) {
    return {
        url: url,
        isCopied: false,
        selectText: function () {
            this.$refs.input.select();
        },
        clipboardCopy: function() {
            navigator.clipboard.writeText(url).then(function () {
                this.isCopied = true;
                this.$refs.button.blur();
                this.selectText();
            }.bind(this));
        }
    }
}