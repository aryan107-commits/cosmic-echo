(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function seededRandom(seed) {
    let value = seed >>> 0;
    return function () {
      value = (value * 1664525 + 1013904223) >>> 0;
      return value / 4294967296;
    };
  }

  function drawSyntheticField(ctx, width, height, mode) {
    const random = seededRandom(20261124);
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#050b14";
    ctx.fillRect(0, 0, width, height);

    const diffuse = mode !== "corrected";
    const clouds = [
      [0.22, 0.32, 0.28, "rgba(66, 92, 132, 0.46)"],
      [0.70, 0.27, 0.30, "rgba(108, 73, 119, 0.35)"],
      [0.55, 0.78, 0.35, "rgba(40, 103, 111, 0.31)"],
      [0.91, 0.69, 0.22, "rgba(131, 91, 59, 0.20)"]
    ];

    if (diffuse) {
      clouds.forEach((cloud) => {
        const x = cloud[0] * width;
        const y = cloud[1] * height;
        const radius = cloud[2] * Math.min(width, height);
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
        gradient.addColorStop(0, cloud[3]);
        gradient.addColorStop(1, "rgba(5, 11, 20, 0)");
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);
      });

      ctx.save();
      ctx.globalAlpha = 0.12;
      ctx.strokeStyle = "#7f9bb5";
      ctx.lineWidth = 0.7;
      for (let i = 1; i < 10; i += 1) {
        const y = (height / 10) * i;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }
      for (let i = 1; i < 14; i += 1) {
        const x = (width / 14) * i;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      ctx.restore();
    }

    const sources = [
      [0.16, 0.21, 0.012], [0.34, 0.55, 0.009], [0.49, 0.29, 0.014],
      [0.63, 0.67, 0.010], [0.79, 0.40, 0.017], [0.87, 0.78, 0.008],
      [0.25, 0.83, 0.007], [0.57, 0.48, 0.006], [0.11, 0.61, 0.006]
    ];

    if (mode !== "background") {
      sources.forEach((source, index) => {
        const x = source[0] * width;
        const y = source[1] * height;
        const radius = source[2] * Math.min(width, height);
        const glow = ctx.createRadialGradient(x, y, 0, x, y, radius * 5.5);
        glow.addColorStop(0, mode === "corrected" ? "rgba(230, 220, 190, .82)" : "rgba(237, 223, 191, .95)");
        glow.addColorStop(0.18, "rgba(164, 185, 207, .28)");
        glow.addColorStop(1, "rgba(164, 185, 207, 0)");
        ctx.fillStyle = glow;
        ctx.beginPath();
        ctx.arc(x, y, radius * 5.5, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = index % 3 === 0 ? "#f2e5c7" : "#d8e2ec";
        ctx.beginPath();
        ctx.arc(x, y, Math.max(1.4, radius * 0.42), 0, Math.PI * 2);
        ctx.fill();
      });
    }

    if (mode === "mask") {
      ctx.save();
      ctx.lineWidth = Math.max(1.3, width / 700);
      sources.forEach((source, index) => {
        const x = source[0] * width;
        const y = source[1] * height;
        const radius = source[2] * Math.min(width, height) * 4.7;
        ctx.fillStyle = "rgba(216, 139, 91, .20)";
        ctx.strokeStyle = "rgba(236, 171, 117, .9)";
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        if (index % 2 === 0) {
          ctx.strokeStyle = "rgba(236, 171, 117, .25)";
          ctx.beginPath();
          ctx.arc(x, y, radius * 1.35, 0, Math.PI * 2);
          ctx.stroke();
        }
      });
      ctx.restore();
    }

    if (mode === "corrected") {
      const veil = ctx.createLinearGradient(0, 0, width, height);
      veil.addColorStop(0, "rgba(4, 11, 19, .12)");
      veil.addColorStop(1, "rgba(11, 24, 34, .18)");
      ctx.fillStyle = veil;
      ctx.fillRect(0, 0, width, height);
    }

    const starCount = Math.floor((width * height) / 5000);
    for (let i = 0; i < starCount; i += 1) {
      const x = random() * width;
      const y = random() * height;
      const radius = random() * 1.05 + 0.25;
      const alpha = random() * 0.52 + 0.15;
      ctx.fillStyle = "rgba(216, 228, 239, " + alpha.toFixed(3) + ")";
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.save();
    ctx.strokeStyle = "rgba(218, 190, 142, .25)";
    ctx.lineWidth = 1;
    ctx.strokeRect(12, 12, width - 24, height - 24);
    ctx.restore();
  }

  function initStarfield() {
    const canvas = document.getElementById("starfield");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const random = seededRandom(44107);
    let stars = [];
    let frame = 0;
    let width = 0;
    let height = 0;

    function resize() {
      const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.floor(width * ratio);
      canvas.height = Math.floor(height * ratio);
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      stars = Array.from({ length: Math.min(130, Math.floor(width / 9)) }, () => ({
        x: random() * width,
        y: random() * height,
        radius: random() * 1.1 + 0.2,
        phase: random() * Math.PI * 2,
        speed: random() * 0.012 + 0.002
      }));
      draw(true);
    }

    function draw(staticFrame) {
      ctx.clearRect(0, 0, width, height);
      stars.forEach((star) => {
        const pulse = staticFrame || reducedMotion ? 0.55 : 0.28 + (Math.sin(frame * star.speed + star.phase) + 1) * 0.22;
        ctx.fillStyle = "rgba(189, 207, 224, " + pulse.toFixed(3) + ")";
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        ctx.fill();
      });
      if (!staticFrame && !reducedMotion) {
        frame += 1;
        window.requestAnimationFrame(() => draw(false));
      }
    }

    resize();
    if (!reducedMotion) window.addEventListener("resize", resize, { passive: true });
  }

  function initHeroField() {
    const canvas = document.getElementById("hero-field");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const buttons = document.querySelectorAll("[data-layer]");
    const labels = {
      raw: "SIGNAL / SYNTHETIC",
      mask: "SOURCE MASK / SYNTHETIC",
      background: "BACKGROUND / SYNTHETIC",
      corrected: "RESIDUAL / SYNTHETIC"
    };

    function selectLayer(mode) {
      drawSyntheticField(ctx, canvas.width, canvas.height, mode);
      buttons.forEach((button) => {
        const active = button.dataset.layer === mode;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-pressed", active ? "true" : "false");
      });
      const centerLabel = document.querySelector(".field-coordinates span:nth-child(2)");
      if (centerLabel) centerLabel.textContent = labels[mode];
    }

    buttons.forEach((button) => {
      button.addEventListener("click", () => selectLayer(button.dataset.layer));
    });
    selectLayer("raw");
  }

  function initWorkbench() {
    const canvas = document.getElementById("workbench-canvas");
    const upload = document.getElementById("image-upload");
    if (!canvas || !upload) return;

    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    const sourceCanvas = document.createElement("canvas");
    sourceCanvas.width = canvas.width;
    sourceCanvas.height = canvas.height;
    const sourceCtx = sourceCanvas.getContext("2d");
    const brightness = document.getElementById("brightness");
    const contrast = document.getElementById("contrast");
    const gamma = document.getElementById("gamma");
    const status = document.getElementById("image-status");
    const state = document.getElementById("preview-state");
    let uploadedName = "";
    let renderQueued = false;

    drawSyntheticField(sourceCtx, sourceCanvas.width, sourceCanvas.height, "raw");

    function drawContainedImage(image) {
      sourceCtx.fillStyle = "#050b14";
      sourceCtx.fillRect(0, 0, sourceCanvas.width, sourceCanvas.height);
      const scale = Math.min(sourceCanvas.width / image.width, sourceCanvas.height / image.height);
      const drawWidth = image.width * scale;
      const drawHeight = image.height * scale;
      const x = (sourceCanvas.width - drawWidth) / 2;
      const y = (sourceCanvas.height - drawHeight) / 2;
      sourceCtx.drawImage(image, x, y, drawWidth, drawHeight);
    }

    function queueRender() {
      if (renderQueued) return;
      renderQueued = true;
      window.requestAnimationFrame(() => {
        renderQueued = false;
        render();
      });
    }

    function render() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(sourceCanvas, 0, 0);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const pixels = imageData.data;
      const b = Number(brightness.value) / 100;
      const c = Number(contrast.value) / 100;
      const g = Number(gamma.value) / 100;
      const inverseGamma = 1 / Math.max(0.1, g);

      for (let i = 0; i < pixels.length; i += 4) {
        for (let channel = 0; channel < 3; channel += 1) {
          let value = pixels[i + channel] / 255;
          value = ((value - 0.5) * c + 0.5) * b;
          value = Math.max(0, Math.min(1, value));
          pixels[i + channel] = Math.round(255 * Math.pow(value, inverseGamma));
        }
      }
      ctx.putImageData(imageData, 0, 0);

      document.getElementById("brightness-value").textContent = brightness.value + "%";
      document.getElementById("contrast-value").textContent = contrast.value + "%";
      document.getElementById("gamma-value").textContent = (Number(gamma.value) / 100).toFixed(2);
      state.textContent = uploadedName ? "LOCAL IMAGE / DISPLAY ADJUSTED" : "ILLUSTRATIVE FIELD / DISPLAY ADJUSTED";
    }

    [brightness, contrast, gamma].forEach((input) => input.addEventListener("input", queueRender));

    upload.addEventListener("change", () => {
      const file = upload.files && upload.files[0];
      if (!file) return;
      if (!/^image\/(png|jpeg|webp)$/.test(file.type)) {
        status.textContent = "UNSUPPORTED FILE TYPE";
        state.textContent = "CHOOSE PNG, JPEG OR WEBP";
        upload.value = "";
        return;
      }
      const objectUrl = URL.createObjectURL(file);
      const image = new Image();
      image.onload = () => {
        drawContainedImage(image);
        uploadedName = file.name;
        status.textContent = file.name.toUpperCase().slice(0, 34);
        state.textContent = "LOCAL IMAGE LOADED";
        URL.revokeObjectURL(objectUrl);
        queueRender();
      };
      image.onerror = () => {
        status.textContent = "IMAGE COULD NOT BE READ";
        state.textContent = "TRY ANOTHER IMAGE";
        URL.revokeObjectURL(objectUrl);
      };
      image.src = objectUrl;
    });

    document.getElementById("reset-display").addEventListener("click", () => {
      brightness.value = "100";
      contrast.value = "100";
      gamma.value = "100";
      queueRender();
    });

    document.getElementById("save-preview").addEventListener("click", () => {
      const link = document.createElement("a");
      link.download = "cosmic-echo-preview.png";
      link.href = canvas.toDataURL("image/png");
      link.click();
      state.textContent = "PREVIEW EXPORTED";
    });

    render();
  }

  function initNavigation() {
    const toggle = document.getElementById("menu-toggle");
    const nav = document.getElementById("primary-nav");
    if (!toggle || !nav) return;

    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") !== "true";
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
      nav.classList.toggle("is-open", open);
    });

    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open navigation");
      });
    });
  }

  function initReveal() {
    const elements = document.querySelectorAll(".reveal");
    if (reducedMotion || !("IntersectionObserver" in window)) {
      elements.forEach((element) => element.classList.add("is-visible"));
      return;
    }
    const observer = new IntersectionObserver((entries, activeObserver) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          activeObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    elements.forEach((element) => observer.observe(element));
  }

  function initYear() {
    const year = document.getElementById("current-year");
    if (year) year.textContent = String(new Date().getFullYear());
  }

  document.addEventListener("DOMContentLoaded", () => {
    initStarfield();
    initHeroField();
    initWorkbench();
    initNavigation();
    initReveal();
    initYear();
  });
})();