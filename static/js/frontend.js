  window.addEventListener('load', () => {
    document.documentElement.style.setProperty(
      '--real-vh', window.innerHeight + 'px'
    );
  });
  window.addEventListener('resize', () => {
    document.documentElement.style.setProperty(
      '--real-vh', window.innerHeight + 'px'
    );
  });
