  if (window.location.search.includes('element_type=main_banner')) {
    window.history.replaceState({}, document.title, window.location.pathname);
  }