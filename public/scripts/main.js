const styleConfigs = {
  transparent: {
    theme: "transparent",
    note: "Visible engineering, softened edges, and a lighter emotional footprint.",
    imageClass: "hero-image-transparent",
  },
  blue: {
    theme: "blue",
    note: "A familiar clinical blue palette for trust, calm, and early institutional adoption.",
    imageClass: "hero-image-blue",
  },
  kintsugi: {
    theme: "kintsugi",
    note: "Warm metallic seams that turn repair into pride and resilience into design language.",
    imageClass: "hero-image-kintsugi",
  },
};

const activateStyle = (style) => {
  const config = styleConfigs[style];
  if (!config) {
    return;
  }

  document.body.dataset.theme = config.theme;

  const buttons = document.querySelectorAll("[data-style]");
  buttons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.style === style);
  });

  const images = document.querySelectorAll(".hero-image");
  images.forEach((image) => {
    image.classList.toggle("is-visible", image.classList.contains(config.imageClass));
  });

  const note = document.querySelector("[data-style-note]");
  if (note) {
    note.textContent = config.note;
  }
};

const initStyleSwitcher = () => {
  const buttons = document.querySelectorAll("[data-style]");
  if (!buttons.length) {
    return;
  }

  buttons.forEach((button) => {
    button.addEventListener("click", () => activateStyle(button.dataset.style));
  });
};

const initReveal = () => {
  const items = document.querySelectorAll("[data-reveal]");
  if (!items.length) {
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-revealed");
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.18,
      rootMargin: "0px 0px -5% 0px",
    },
  );

  items.forEach((item, index) => {
    item.style.transitionDelay = `${Math.min(index * 70, 280)}ms`;
    observer.observe(item);
  });
};

activateStyle(document.body.dataset.theme || "transparent");
initStyleSwitcher();
initReveal();
