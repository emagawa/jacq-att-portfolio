// ==========================================================================
// Jacqueline Magawa — Portfolio JS
// ==========================================================================

document.getElementById("year").textContent = new Date().getFullYear();

/* ---------- Nav: scroll state, mobile toggle, active link ---------- */
const siteNav = document.getElementById("siteNav");
const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");

window.addEventListener(
        "scroll",
        () => {
                siteNav.classList.toggle("scrolled", window.scrollY > 40);
        },
        { passive: true },
);

navToggle.addEventListener("click", () => {
        navToggle.classList.toggle("open");
        navLinks.classList.toggle("open");
});

navLinks.querySelectorAll("a").forEach((a) => {
        a.addEventListener("click", () => {
                navToggle.classList.remove("open");
                navLinks.classList.remove("open");
        });
});

const sections = document.querySelectorAll("section[id]");
const navItems = document.querySelectorAll(".nav-link");
const navObserver = new IntersectionObserver(
        (entries) => {
                entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                                navItems.forEach((a) =>
                                        a.classList.toggle(
                                                "active",
                                                a.getAttribute("href") === "#" + entry.target.id,
                                        ),
                                );
                        }
                });
        },
        { rootMargin: "-45% 0px -50% 0px" },
);
sections.forEach((s) => navObserver.observe(s));

/* ---------- Hero entrance (scroll cue only; hero uses CSS animation) ---------- */
window.addEventListener("DOMContentLoaded", () => {
        const cue = document.querySelector(".scroll-cue");
        if (cue)
                setTimeout(() => {
                        cue.style.transition = "opacity .8s ease";
                        cue.style.opacity = "1";
                }, 900);
});

/* ---------- Marquee ---------- */
const marqueePhrases = [
        "Aviation Enthusiast",
        "Cybersecurity Student",
        "FAA Student Pilot",
        "Computer Science",
        "Albany, NY",
        "Open to Internships",
];
const marqueeTrack = document.getElementById("marqueeTrack");
if (marqueeTrack) {
        // Two copies for a seamless -50% loop
        const once = marqueePhrases
                .map((p) => `<span class="marquee-item">${p}</span>`)
                .join("");
        marqueeTrack.innerHTML = once + once;
}

/* ---------- Reveal on scroll ---------- */
const revealObserver = new IntersectionObserver(
        (entries) => {
                entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                                entry.target.classList.add("in");
                                revealObserver.unobserve(entry.target);
                        }
                });
        },
        { threshold: 0.12 },
);

function observeReveal(el, i = 0) {
        el.style.transitionDelay = (i % 6) * 55 + "ms";
        revealObserver.observe(el);
}

document.querySelectorAll(".reveal").forEach((el, i) => observeReveal(el, i));

/* ---------- Training Films ---------- */
const films = [
        {
                slug: "first-flight-brookhaven-2015",
                title: "First Flight — Brookhaven Airport",
                meta: "16 May 2015 · Shirley, NY",
                desc: "Her very first flight, front seat, with a certified flight instructor.",
        },
        {
                slug: "first-taxi-brookhaven-2015",
                title: "First Taxi & Takeoff Roll",
                meta: "17 May 2015 · Brookhaven Airport",
                desc: "Ground handling and takeoff-roll practice the very next day.",
        },
        {
                slug: "taxi-training-republic-2015",
                title: "Taxi & Ground Training",
                meta: "28 Nov 2015 · Republic Airport, Farmingdale",
                desc: "Continued ground training with the Brookhaven Aviation Flying Club.",
        },
        {
                slug: "midair-training-republic-2019",
                title: "Mid-Air Training",
                meta: "17 Aug 2019 · Republic Airport, Farmingdale",
                desc: "Hands-on instrument and control work, four years into training.",
        },
        {
                slug: "farmingdale-edgartown-2019",
                title: "Cross-Country: Farmingdale → Edgartown",
                meta: "31 Aug 2019 · with Instructor Alfred James",
                desc: "A cross-country training flight out to Martha's Vineyard.",
        },
];

const filmsGrid = document.getElementById("filmsGrid");
films.forEach((f, i) => {
        const card = document.createElement("div");
        card.className = "film-card reveal";
        card.setAttribute("data-testid", `film-card-${i}`);
        card.innerHTML = `
    <div class="film-media" data-slug="${f.slug}" data-testid="film-media-${i}">
      <img src="assets/video/posters/${f.slug}.jpg" alt="${f.title}" loading="lazy">
      <div class="film-play">
        <svg viewBox="0 0 24 24" fill="rgba(255,255,255,0.95)"><circle cx="12" cy="12" r="11" fill="rgba(8,21,33,0.5)" stroke="rgba(255,255,255,0.85)" stroke-width="1"/><path d="M10 8l6 4-6 4V8z"/></svg>
      </div>
    </div>
    <div class="film-body">
      <div class="card-meta">${f.meta}</div>
      <h4>${f.title}</h4>
      <p>${f.desc}</p>
    </div>`;
        filmsGrid.appendChild(card);
        observeReveal(card, i);
});

filmsGrid.addEventListener("click", (e) => {
        const media = e.target.closest(".film-media");
        if (!media) return;
        const slug = media.dataset.slug;
        const video = document.createElement("video");
        video.src = `assets/video/${slug}.mp4`;
        video.controls = true;
        video.autoplay = true;
        video.playsInline = true;
        media.innerHTML = "";
        media.appendChild(video);
});

/* ---------- Gallery ---------- */
const galleryData = [
        { file: "g00-redacted.jpg", title: "FAA Student Pilot Certificate", desc: "Issued 26 Aug 2021 \u2014 personal details redacted for privacy." },
        { file: "g04.jpg", title: "Instrument briefing", desc: "Walking through the panel before a training flight." },
        { file: "g07.jpg", title: "Flight-school recognition", desc: "Recognized for her progress at Brookhaven Aviation." },
        { file: "g09.jpg", title: "Canopy view", desc: "Wheels up over the Long Island coastline." },
        { file: "g16.jpg", title: "Martha's Vineyard Airport", desc: "General Aviation ramp, mid cross-country trip." },
        { file: "g17.jpg", title: "Cabin check", desc: "Settling in before a training leg out of Republic Airport." },
        { file: "g19.jpg", title: "Downwind", desc: "Looking out over the field on approach." },
        { file: "g20.jpg", title: "Hands on the yoke", desc: "Working the panel during a lesson." },
        { file: "g23.jpg", title: "Outstanding Academic Excellence", desc: "Presidential Education Awards recognition." },
        { file: "g31.jpg", title: "Above the coastline", desc: "A training flight along the New York shoreline." },
        { file: "g34.jpg", title: "Ramp crew", desc: "With instructors after a cross-country flight." },
        { file: "g36.jpg", title: "On the ramp", desc: "Preflight at Republic Airport, Farmingdale." },
        { file: "g39.jpg", title: "High above", desc: "Cruising altitude on a clear-sky training day." },
        { file: "g41.jpg", title: "Quiet ramp", desc: "A parked trainer at rest between lessons." },
        { file: "g42.jpg", title: "Eyes on the horizon", desc: "In the cockpit, mid-flight." },
        { file: "g44.jpg", title: "Working the checklist", desc: "Hands-on with the avionics." },
        { file: "g47.jpg", title: "Panel scan", desc: "Reading instruments during climb-out." },
        { file: "g48.jpg", title: "Experimental class", desc: "Riding along in an experimental-category aircraft." },
        { file: "g53.jpg", title: "With her instructor", desc: "A moment with the team at Brookhaven Aviation." },
        { file: "g58.jpg", title: "Young Eagles Certificate", desc: "EAA Young Eagles \u2014 the flight that started it all." },
        { file: "g60.jpg", title: "Cleared for taxi", desc: "Celebrating on the ramp after a lesson." },
        { file: "g61.jpg", title: "Cockpit door", desc: "Sharing the moment with an instructor." },
        { file: "g63.jpg", title: "Hands-on training", desc: "Working the yoke with an instructor alongside." },
        { file: "g69.jpg", title: "With Instructor Alfred James", desc: "Preflight at Republic Airport, Farmingdale." },
        { file: "g70.jpg", title: "At the controls", desc: "A quick look back before heading out." },
        { file: "g71.jpg", title: "Young Eagles day", desc: "With her flight instructor after the certificate ceremony." },
];
const galleryGrid = document.getElementById("galleryGrid");
galleryData.forEach((g, i) => {
        const item = document.createElement("div");
        item.className = "gallery-item reveal";
        item.dataset.index = i;
        item.setAttribute("data-testid", `gallery-item-${i}`);
        item.innerHTML = `
    <img src="assets/gallery/thumb/${g.file}" alt="${g.title}" loading="lazy">
    <div class="gallery-cap"><b>${g.title}</b><span>${g.desc}</span></div>
  `;
        galleryGrid.appendChild(item);
        observeReveal(item, i);
});

/* ---------- Lightbox ---------- */
const lightbox = document.getElementById("lightbox");
const lightboxImg = document.getElementById("lightboxImg");
const lightboxTitle = document.getElementById("lightboxTitle");
const lightboxDesc = document.getElementById("lightboxDesc");
let currentIndex = 0;

function openLightbox(i) {
        currentIndex = i;
        const g = galleryData[i];
        lightboxImg.src = `assets/gallery/full/${g.file}`;
        lightboxImg.alt = g.title;
        lightboxTitle.textContent = g.title;
        lightboxDesc.textContent = g.desc;
        lightbox.classList.add("open");
        document.body.style.overflow = "hidden";
}
function closeLightbox() {
        lightbox.classList.remove("open");
        document.body.style.overflow = "";
}
function showRelative(delta) {
        currentIndex =
                (currentIndex + delta + galleryData.length) % galleryData.length;
        openLightbox(currentIndex);
}

galleryGrid.addEventListener("click", (e) => {
        const item = e.target.closest(".gallery-item");
        if (!item) return;
        openLightbox(parseInt(item.dataset.index, 10));
});
document.getElementById("lightboxClose").addEventListener("click", closeLightbox);
document.getElementById("lightboxPrev").addEventListener("click", () => showRelative(-1));
document.getElementById("lightboxNext").addEventListener("click", () => showRelative(1));
lightbox.addEventListener("click", (e) => {
        if (e.target === lightbox) closeLightbox();
});
document.addEventListener("keydown", (e) => {
        if (!lightbox.classList.contains("open")) return;
        if (e.key === "Escape") closeLightbox();
        if (e.key === "ArrowLeft") showRelative(-1);
        if (e.key === "ArrowRight") showRelative(1);
});

/* ---------- Contact form -> backend (Resend email) ---------- */
const contactForm = document.getElementById("contactForm");
const cfNote = document.getElementById("cfNote");
const cfSubmit = document.getElementById("cfSubmit");

contactForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = {
                name: document.getElementById("cf-name").value.trim(),
                email: document.getElementById("cf-email").value.trim(),
                subject: document.getElementById("cf-subject").value.trim(),
                message: document.getElementById("cf-message").value.trim(),
                website: document.getElementById("cf-website").value.trim(),
        };

        if (!payload.name || !payload.email || !payload.message) {
                cfNote.textContent = "Please fill in your name, email, and message.";
                cfNote.className = "form-note err";
                return;
        }

        cfSubmit.disabled = true;
        const original = cfSubmit.textContent;
        cfSubmit.textContent = "Sending…";
        cfNote.textContent = "";
        cfNote.className = "form-note";

        try {
                const res = await fetch("/api/contact", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload),
                });
                const data = await res.json().catch(() => ({}));
                if (res.ok) {
                        contactForm.reset();
                        cfNote.textContent =
                                data.message || "Thanks — your message has been sent.";
                        cfNote.className = "form-note ok";
                } else {
                        cfNote.textContent =
                                data.detail ||
                                "Couldn't send right now. Please email jacq.magawa@gmail.com directly.";
                        cfNote.className = "form-note err";
                }
        } catch (err) {
                cfNote.textContent =
                        "Network error. Please email jacq.magawa@gmail.com directly.";
                cfNote.className = "form-note err";
        } finally {
                cfSubmit.disabled = false;
                cfSubmit.textContent = original;
        }
});
