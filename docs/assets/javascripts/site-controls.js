(function () {
  "use strict";

  const storageKeys = {
    navHidden: "s1-reader-nav-hidden",
    textSize: "s1-reader-text-size",
    lineHeight: "s1-reader-line-height",
    contentWidth: "s1-reader-content-width",
    tocHidden: "s1-reader-toc-hidden"
  };

  const defaults = {
    textSize: 100,
    lineHeight: 165,
    contentWidth: 52
  };

  const menuIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18v2H3V6m0 5h18v2H3v-2m0 5h18v2H3v-2Z"></path></svg>';
  const closeIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41Z"></path></svg>';
  const minusIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 13H5v-2h14v2Z"></path></svg>';
  const plusIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2Z"></path></svg>';

  function readNumber(key, fallback, min, max) {
    const stored = localStorage.getItem(key);
    if (stored === null) return fallback;
    const value = Number(stored);
    return Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : fallback;
  }

  function applyPreferences() {
    const root = document.documentElement;
    const textSize = readNumber(storageKeys.textSize, defaults.textSize, 85, 140);
    const lineHeight = readNumber(storageKeys.lineHeight, defaults.lineHeight, 140, 200);
    const contentWidth = readNumber(storageKeys.contentWidth, defaults.contentWidth, 42, 78);

    root.style.setProperty("--reader-font-scale", textSize / 100);
    root.style.setProperty("--reader-line-height", lineHeight / 100);
    root.style.setProperty("--reader-content-width", contentWidth + "rem");
    root.classList.toggle("reader-nav-hidden", localStorage.getItem(storageKeys.navHidden) === "true");
    root.classList.toggle("reader-toc-hidden", localStorage.getItem(storageKeys.tocHidden) === "true");
  }

  function button(className, label, contents) {
    const element = document.createElement("button");
    element.type = "button";
    element.className = className;
    element.setAttribute("aria-label", label);
    element.title = label;
    element.innerHTML = contents;
    return element;
  }

  function setPressed(element, pressed) {
    element.setAttribute("aria-pressed", String(pressed));
  }

  function createReaderControls() {
    const header = document.querySelector(".md-header__inner");
    if (!header || header.querySelector(".reader-controls")) return;

    const controls = document.createElement("div");
    controls.className = "reader-controls";

    const navButton = button("reader-control reader-control--nav", "Hide navigation menu", menuIcon);
    const settingsButton = button("reader-control reader-control--settings", "Reading settings", "<span aria-hidden=\"true\">Aa</span>");
    settingsButton.setAttribute("aria-expanded", "false");

    const panel = document.createElement("div");
    panel.className = "reader-settings";
    panel.hidden = true;
    panel.innerHTML = `
      <div class="reader-settings__header">
        <strong>Reading settings</strong>
        <button type="button" class="reader-settings__close" aria-label="Close reading settings" title="Close reading settings">${closeIcon}</button>
      </div>
      <label class="reader-setting">
        <span>Text size <output data-output="textSize"></output></span>
        <input data-setting="textSize" type="range" min="85" max="140" step="5">
      </label>
      <label class="reader-setting">
        <span>Line spacing <output data-output="lineHeight"></output></span>
        <input data-setting="lineHeight" type="range" min="140" max="200" step="5">
      </label>
      <label class="reader-setting">
        <span>Page width <output data-output="contentWidth"></output></span>
        <input data-setting="contentWidth" type="range" min="42" max="78" step="2">
      </label>
      <label class="reader-setting reader-setting--toggle">
        <span>Show page outline</span>
        <input data-setting="tocHidden" type="checkbox">
      </label>
      <button type="button" class="reader-settings__reset">Reset reading settings</button>`;

    controls.append(navButton, settingsButton, panel);
    header.appendChild(controls);

    const syncPanel = () => {
      const values = {
        textSize: readNumber(storageKeys.textSize, defaults.textSize, 85, 140),
        lineHeight: readNumber(storageKeys.lineHeight, defaults.lineHeight, 140, 200),
        contentWidth: readNumber(storageKeys.contentWidth, defaults.contentWidth, 42, 78)
      };
      Object.entries(values).forEach(([name, value]) => {
        panel.querySelector(`[data-setting="${name}"]`).value = value;
      });
      panel.querySelector('[data-setting="tocHidden"]').checked = localStorage.getItem(storageKeys.tocHidden) !== "true";
      panel.querySelector('[data-output="textSize"]').value = values.textSize + "%";
      panel.querySelector('[data-output="lineHeight"]').value = (values.lineHeight / 100).toFixed(2);
      panel.querySelector('[data-output="contentWidth"]').value = values.contentWidth + " rem";
      const navHidden = document.documentElement.classList.contains("reader-nav-hidden");
      setPressed(navButton, navHidden);
      navButton.setAttribute("aria-label", navHidden ? "Show navigation menu" : "Hide navigation menu");
      navButton.title = navButton.getAttribute("aria-label");
    };

    const closePanel = () => {
      panel.hidden = true;
      settingsButton.setAttribute("aria-expanded", "false");
    };

    navButton.addEventListener("click", () => {
      const hidden = document.documentElement.classList.toggle("reader-nav-hidden");
      localStorage.setItem(storageKeys.navHidden, String(hidden));
      syncPanel();
    });

    settingsButton.addEventListener("click", () => {
      panel.hidden = !panel.hidden;
      settingsButton.setAttribute("aria-expanded", String(!panel.hidden));
      if (!panel.hidden) panel.querySelector("input").focus();
    });
    panel.querySelector(".reader-settings__close").addEventListener("click", closePanel);

    panel.addEventListener("input", (event) => {
      const input = event.target.closest("[data-setting]");
      if (!input) return;
      if (input.dataset.setting === "tocHidden") {
        const hidden = !input.checked;
        localStorage.setItem(storageKeys.tocHidden, String(hidden));
      } else {
        localStorage.setItem(storageKeys[input.dataset.setting], input.value);
      }
      applyPreferences();
      syncPanel();
    });

    panel.querySelector(".reader-settings__reset").addEventListener("click", () => {
      [storageKeys.textSize, storageKeys.lineHeight, storageKeys.contentWidth, storageKeys.tocHidden].forEach((key) => localStorage.removeItem(key));
      applyPreferences();
      syncPanel();
    });

    document.addEventListener("pointerdown", (event) => {
      if (!panel.hidden && !controls.contains(event.target)) closePanel();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !panel.hidden) {
        closePanel();
        settingsButton.focus();
      }
    });
    syncPanel();
  }

  let viewer = null;
  let diagramObserver = null;
  let diagramTimer = null;

  function closeDiagram() {
    if (!viewer) return;
    viewer.placeholder.replaceWith(viewer.diagram);
    viewer.diagram.classList.remove("diagram-viewer__diagram");
    if (viewer.originalStyle === null) viewer.diagram.removeAttribute("style");
    else viewer.diagram.setAttribute("style", viewer.originalStyle);
    viewer.overlay.remove();
    document.documentElement.classList.remove("diagram-viewer-open");
    viewer.diagram.focus();
    viewer = null;
  }

  function openDiagram(diagram) {
    if (viewer || diagram.closest(".diagram-viewer")) return;
    const placeholder = document.createComment("diagram location");
    const originalStyle = diagram.getAttribute("style");
    diagram.replaceWith(placeholder);

    const overlay = document.createElement("div");
    overlay.className = "diagram-viewer";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "Diagram viewer");
    overlay.innerHTML = `
      <div class="diagram-viewer__toolbar" role="toolbar" aria-label="Diagram zoom controls">
        <button type="button" data-action="out" aria-label="Zoom out" title="Zoom out">${minusIcon}</button>
        <output class="diagram-viewer__zoom" aria-live="polite">100%</output>
        <button type="button" data-action="in" aria-label="Zoom in" title="Zoom in">${plusIcon}</button>
        <button type="button" data-action="reset">Reset</button>
        <button type="button" data-action="close" aria-label="Close diagram" title="Close diagram">${closeIcon}</button>
      </div>
      <div class="diagram-viewer__canvas"></div>`;

    const canvas = overlay.querySelector(".diagram-viewer__canvas");
    diagram.classList.add("diagram-viewer__diagram");
    canvas.appendChild(diagram);
    document.body.appendChild(overlay);
    document.documentElement.classList.add("diagram-viewer-open");
    viewer = { overlay, diagram, placeholder, originalStyle, zoom: 1 };

    const setZoom = (next) => {
      viewer.zoom = Math.min(3, Math.max(0.75, next));
      diagram.style.width = (viewer.zoom * 100) + "%";
      overlay.querySelector(".diagram-viewer__zoom").value = Math.round(viewer.zoom * 100) + "%";
    };

    overlay.addEventListener("click", (event) => {
      const action = event.target.closest("[data-action]")?.dataset.action;
      if (action === "in") setZoom(viewer.zoom + 0.25);
      if (action === "out") setZoom(viewer.zoom - 0.25);
      if (action === "reset") setZoom(1);
      if (action === "close") closeDiagram();
    });
    canvas.addEventListener("wheel", (event) => {
      if (!event.ctrlKey) return;
      event.preventDefault();
      setZoom(viewer.zoom + (event.deltaY < 0 ? 0.25 : -0.25));
    }, { passive: false });
    overlay.querySelector('[data-action="close"]').focus();
  }

  function prepareDiagrams() {
    const diagrams = [...document.querySelectorAll(".md-content .mermaid")];
    diagrams.forEach((diagram) => {
      // Material replaces the source <pre> with a rendered <div>. A DOM property,
      // unlike a data attribute, is not copied to that replacement element.
      if (diagram.tagName !== "DIV" || diagram.viewerReady) return;
      diagram.viewerReady = true;
      diagram.dataset.viewerReady = "true";
      diagram.tabIndex = 0;
      diagram.setAttribute("role", "button");
      diagram.setAttribute("aria-label", "Open diagram viewer");
      diagram.title = "Open diagram viewer";
    });
    return diagrams.some((diagram) => diagram.tagName !== "DIV" || !diagram.viewerReady);
  }

  function initializePage() {
    if (viewer) closeDiagram();
    applyPreferences();
    createReaderControls();
    prepareDiagrams();
    if (diagramObserver) diagramObserver.disconnect();
    if (diagramTimer) window.clearInterval(diagramTimer);
    if (document.body) {
      diagramObserver = new MutationObserver(prepareDiagrams);
      diagramObserver.observe(document.body, { childList: true, subtree: true });
      // Mermaid renders asynchronously and may replace its host after the page
      // mutation has completed. This small check also covers slow CDN loads.
      diagramTimer = window.setInterval(() => {
        if (!prepareDiagrams()) {
          window.clearInterval(diagramTimer);
          diagramTimer = null;
        }
      }, 1000);
    }
  }

  window.addEventListener("click", (event) => {
    const diagram = event.composedPath().find((element) =>
      element instanceof Element && element.matches(".md-content .mermaid")
    );
    if (diagram && !viewer && !diagram.closest(".diagram-viewer")) openDiagram(diagram);
  }, true);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && viewer) return closeDiagram();
    const diagram = event.composedPath().find((element) =>
      element instanceof Element && element.matches(".md-content .mermaid")
    );
    if (diagram && !viewer && (event.key === "Enter" || event.key === " ")) {
      event.preventDefault();
      openDiagram(diagram);
    }
  });

  applyPreferences();
  if (typeof document$ !== "undefined") document$.subscribe(initializePage);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initializePage);
  else initializePage();
}());
