// Responsible for preventing micro:bit code samples from beginning to load until they are scrolled to

let options = {
    rootMargin: '0px',
    threshold: 0.5
}

let callback = (entries, observer) => {
    entries.forEach(element => {
        element.target.style.display = "none";
        //{{ code_url|safe }}
    })
}

let observer = new IntersectionObserver(callback, options);

let code_embeds = document.querySelector(".makecode-embed");

code_embeds.forEach(element => {
    observer.observe(element);
})





