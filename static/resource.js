// Responsible for preventing micro:bit code samples from beginning to load until they are scrolled
// down to, preventing large bandwidth use on page load and Firefox's (occasional) odd jumping
// behaviour when an iframe loads its content.

let options = {
    rootMargin: '0px',
    threshold: 0.5
}

let callback = (entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.querySelector(".makecode-frame").src = entry.target.getAttribute("makecode-src");
        }
    })
}

let observer = new IntersectionObserver(callback, options);

let code_embeds = document.querySelectorAll(".makecode-embed");

code_embeds.forEach(element => {
    observer.observe(element);
})





