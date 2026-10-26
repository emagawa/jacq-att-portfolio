// ==========================================================================
// Jacqueline Magawa — Portfolio JS (shared by every page)
// ==========================================================================

/* ---------- Legacy one-page anchors -> dedicated pages ---------- */
const LEGACY_HASHES = {
        "#about": "/about.html",
        "#log": "/flight-log.html",
        "#education": "/education.html",
        "#skills": "/skills.html",
        "#projects": "/projects.html",
        "#films": "/training-films.html",
        "#gallery": "/gallery.html",
        "#contact": "/contact.html",
};
if (document.body.dataset.page === "home" && LEGACY_HASHES[location.hash]) {
        location.replace(LEGACY_HASHES[location.hash]);
}

/* ---------- Unknown URLs served the homepage by the host: keep them out of Google ---------- */
const KNOWN_PATHS = ["/", "/index.html"];
if (document.body.dataset.page === "home" && !KNOWN_PATHS.includes(location.pathname)) {
        const robots = document.querySelector('meta[name="robots"]');
        if (robots) robots.setAttribute("content", "noindex, follow");
}

const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

/* ---------- Nav: scroll state, mobile toggle ---------- */
const siteNav = document.getElementById("siteNav");
const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");
const backToTop = document.getElementById("backToTop");

if (backToTop)
        backToTop.addEventListener("click", () => {
                window.scrollTo({ top: 0, behavior: "smooth" });
        });

function onScroll() {
        siteNav.classList.toggle("scrolled", window.scrollY > 40);
        if (backToTop) backToTop.classList.toggle("show", window.scrollY > 400);
}
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

function setMenu(open) {
        navToggle.classList.toggle("open", open);
        navLinks.classList.toggle("open", open);
        navToggle.setAttribute("aria-expanded", String(open));
}
navToggle.addEventListener("click", () => setMenu(!navLinks.classList.contains("open")));
navLinks.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setMenu(false)));

/* ---------- Hero scroll cue ---------- */
const cue = document.querySelector(".scroll-cue");
if (cue)
        setTimeout(() => {
                cue.style.transition = "opacity .8s ease";
                cue.style.opacity = "1";
        }, 900);

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
        { threshold: 0 },
);
document.querySelectorAll(".reveal").forEach((el, i) => {
        el.style.transitionDelay = (i % 6) * 55 + "ms";
        revealObserver.observe(el);
});

/* Safety fallback: never leave content invisible */
function revealVisible() {
        document.querySelectorAll(".reveal:not(.in)").forEach((el) => {
                if (el.getBoundingClientRect().top < window.innerHeight + 40) el.classList.add("in");
        });
}
window.addEventListener("load", () => setTimeout(revealVisible, 500));
window.addEventListener("scroll", revealVisible, { passive: true });

/* Enter / Space activates role="button" cards */
function onActivate(el, handler) {
        el.addEventListener("click", handler);
        el.addEventListener("keydown", (e) => {
                if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        handler();
                }
        });
}

/* ---------- Training Films (cards are pre-rendered in HTML) ---------- */
document.querySelectorAll(".film-media[data-slug]").forEach((media) => {
        const src = `/assets/video/${media.dataset.slug}.mp4`;
        let preview = null;

        function stopPreview() {
                if (!preview) return;
                preview.pause();
                preview.remove();
                preview = null;
        }

        media.addEventListener("mouseenter", () => {
                if (media.classList.contains("is-playing") || preview) return;
                preview = document.createElement("video");
                preview.src = src;
                preview.muted = true;
                preview.loop = true;
                preview.playsInline = true;
                preview.preload = "auto";
                preview.className = "film-preview";
                media.appendChild(preview);
                media.classList.add("is-preview");
                preview.play().catch(() => {});
        });

        media.addEventListener("mouseleave", () => {
                if (media.classList.contains("is-playing")) return;
                stopPreview();
                media.classList.remove("is-preview");
        });

        onActivate(media, () => {
                if (media.classList.contains("is-playing")) return;
                stopPreview();
                const video = document.createElement("video");
                video.src = src;
                video.controls = true;
                video.autoplay = true;
                video.playsInline = true;
                video.className = "film-fullvideo";
                media.querySelector(".film-play")?.remove();
                media.classList.remove("is-preview");
                media.classList.add("is-playing");
                media.removeAttribute("role");
                media.removeAttribute("tabindex");
                media.appendChild(video);
                video.play().catch(() => {});
        });
});

/* ---------- Gallery lightbox ---------- */
const galleryItems = Array.from(document.querySelectorAll(".gallery-item[data-file]"));
const lightbox = document.getElementById("lightbox");
if (lightbox && galleryItems.length) {
        const lightboxImg = document.getElementById("lightboxImg");
        const lightboxTitle = document.getElementById("lightboxTitle");
        const lightboxDesc = document.getElementById("lightboxDesc");
        let currentIndex = 0;

        const openLightbox = (i) => {
                currentIndex = i;
                const item = galleryItems[i];
                lightboxImg.src = `/assets/gallery/full/${item.dataset.file}`;
                lightboxImg.alt = item.querySelector("img").alt;
                lightboxTitle.textContent = item.querySelector(".gallery-cap b").textContent;
                lightboxDesc.textContent = item.querySelector(".gallery-cap span").textContent;
                lightbox.classList.add("open");
                document.body.style.overflow = "hidden";
        };
        const closeLightbox = () => {
                lightbox.classList.remove("open");
                document.body.style.overflow = "";
        };
        const showRelative = (delta) =>
                openLightbox((currentIndex + delta + galleryItems.length) % galleryItems.length);

        galleryItems.forEach((item, i) => onActivate(item, () => openLightbox(i)));
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
}

/* ---------- Résumé preview + tracking ---------- */
const RESUME_PDF = "/assets/resume-jacqueline-magawa.pdf";

function trackResume(event) {
        try {
                const body = JSON.stringify({ event });
                if (navigator.sendBeacon) {
                        navigator.sendBeacon("/api/track/resume", new Blob([body], { type: "application/json" }));
                } else {
                        fetch("/api/track/resume", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body,
                                keepalive: true,
                        }).catch(() => {});
                }
        } catch (e) {}
}

document.querySelectorAll('a[href$="resume-jacqueline-magawa.pdf"]').forEach((link) => {
        link.addEventListener("click", () => trackResume("download"));
});

const resumeModal = document.getElementById("resumeModal");
if (resumeModal) {
        const resumeFrameWrap = document.getElementById("resumeFrameWrap");
        const openResume = () => {
                if (!resumeFrameWrap.querySelector("iframe")) {
                        const frame = document.createElement("iframe");
                        frame.src = `${RESUME_PDF}#view=FitH`;
                        frame.title = "Résumé — Jacqueline Magawa";
                        frame.setAttribute("data-testid", "resume-iframe");
                        resumeFrameWrap.appendChild(frame);
                }
                resumeModal.classList.add("open");
                document.body.style.overflow = "hidden";
                trackResume("preview");
        };
        const closeResume = () => {
                resumeModal.classList.remove("open");
                document.body.style.overflow = "";
        };
        document.querySelectorAll("[data-resume-open]").forEach((btn) => {
                btn.addEventListener("click", (e) => {
                        e.preventDefault();
                        openResume();
                });
        });
        document.getElementById("resumeClose").addEventListener("click", closeResume);
        resumeModal.addEventListener("click", (e) => {
                if (e.target === resumeModal) closeResume();
        });
        document.addEventListener("keydown", (e) => {
                if (e.key === "Escape" && resumeModal.classList.contains("open")) closeResume();
        });
}

/* ---------- Contact form -> backend (Resend email) ---------- */
const CONTACT_ENDPOINT = "/api/contact";
const contactForm = document.getElementById("contactForm");
if (contactForm) {
        const cfNote = document.getElementById("cfNote");
        const cfSubmit = document.getElementById("cfSubmit");
        const val = (id) => document.getElementById(id).value.trim();

        contactForm.addEventListener("submit", async (e) => {
                e.preventDefault();
                const payload = {
                        name: val("cf-name"),
                        email: val("cf-email"),
                        subject: val("cf-subject"),
                        message: val("cf-message"),
                        website: val("cf-website"),
                };
                if (!payload.name || !payload.email || !payload.message) {
                        cfNote.textContent = "Please fill in your name, email, and message.";
                        cfNote.className = "form-note err";
                        return;
                }
                cfSubmit.disabled = true;
                const original = cfSubmit.innerHTML;
                cfSubmit.textContent = "Sending…";
                cfNote.textContent = "";
                cfNote.className = "form-note";
                try {
                        const res = await fetch(CONTACT_ENDPOINT, {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify(payload),
                        });
                        const data = await res.json().catch(() => ({}));
                        if (res.ok) {
                                contactForm.reset();
                                cfNote.textContent = data.message || "Thanks — your message has been sent.";
                                cfNote.className = "form-note ok";
                        } else {
                                cfNote.textContent =
                                        data.detail || "Couldn't send right now. Please email jacqmagawa.ernest@gmail.com directly.";
                                cfNote.className = "form-note err";
                        }
                } catch (err) {
                        cfNote.textContent = "Network error. Please email jacqmagawa.ernest@gmail.com directly.";
                        cfNote.className = "form-note err";
                } finally {
                        cfSubmit.disabled = false;
                        cfSubmit.innerHTML = original;
                }
        });
}

/* ---------- Custom cursor: smooth dot ---------- */
const cursorDot = document.getElementById("cursorDot");
if (cursorDot && window.matchMedia("(pointer: fine)").matches) {
        let mouseX = window.innerWidth / 2;
        let mouseY = window.innerHeight / 2;
        let dotX = mouseX,
                dotY = mouseY;
        let visible = false;
        const HALF = 4.5;
        const EASE = 0.15;

        window.addEventListener(
                "mousemove",
                (e) => {
                        mouseX = e.clientX;
                        mouseY = e.clientY;
                        if (!visible) {
                                visible = true;
                                cursorDot.classList.add("is-visible");
                        }
                },
                { passive: true },
        );
        document.addEventListener("mouseleave", () => {
                visible = false;
                cursorDot.classList.remove("is-visible");
        });

        function renderCursor() {
                dotX += (mouseX - dotX) * EASE;
                dotY += (mouseY - dotY) * EASE;
                cursorDot.style.transform = "translate3d(" + (dotX - HALF) + "px, " + (dotY - HALF) + "px, 0)";
                requestAnimationFrame(renderCursor);
        }
        requestAnimationFrame(renderCursor);

        document.querySelectorAll("a, button, [role='button']").forEach((el) => {
                el.addEventListener("mouseenter", () => cursorDot.classList.add("is-hover"));
                el.addEventListener("mouseleave", () => cursorDot.classList.remove("is-hover"));
        });
}
