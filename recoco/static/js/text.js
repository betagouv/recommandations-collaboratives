function textFoldToggle(id) {
    var excerpt = document.getElementById("excerpt-" + id);
    var moreText = document.getElementById("more-" + id);
    var btnText = document.getElementById("foldBtn-" + id);

    if (moreText.style.display === "inline") {
        excerpt.style.display = "inline";
        btnText.innerHTML = "[Lire tout]";
        moreText.style.display = "none";
    } else {
        excerpt.style.display = "none";
        btnText.innerHTML = "[Réduire]";
        moreText.style.display = "inline";
    }
}
